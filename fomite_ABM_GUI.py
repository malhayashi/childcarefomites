import numpy as np
import networkx as nx
import random as pr
import matplotlib.pyplot as pl
import pp
import time
import copy
import sys
import os
import PIL
from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
from math import *
from PIL import Image
from PIL import ImageTk

'''
Notes:

do I really need an explicit "contaminated" compartment?
-- might cause unnecessary accounting
-- but checking for contamination is also slow

pre-calculate time to clearance using neg exp for each person/fomite
-- discrete neg exp equivalent?

multi-fomite model/bi-partite human/fomite networkx

output options

'''

global image1
global image2

def run_model(m):
    m.run()
    return np.array(m.output)

class Agent(object):
    def __init__(self, id, state=0, contamination=0, neighbors=[], recoverytime=0):
        self.id = id
        self.state = state # 0: S, 1: C, 2: I1, 3: I2, 4: R
        self.contamination = contamination
        self.timestamp = 0
        self.neighbors = neighbors
        self.fomiteNeighbors = []
        self.recoveryTime = recoverytime

    def pathogen_decay(self,t,r):
        x = self.contamination*exp(-r*(t-self.timestamp))
        self.contamination = max(x,0)

class Fomite(object):
    def __init__(self, id, contamination=0, neighbors=[], decon=None):
        self.id = id
        self.contamination = contamination
        self.timestamp = 0
        self.neighbors = neighbors
        self.decon = decon  # Allows arbitrary decontamination schedule functions

    def pathogen_decay(self,t,r):
        x = self.contamination*exp(-r*(t-self.timestamp))
        self.contamination = max(x,0)

class Model(object):

    def __init__(self,agents,fomites,endtime,contactnetwork,param):
        self.agentDict = {a.id: a for a in agents}
        self.N = len(self.agentDict.keys())
        ### Initialize rate parameters
        self.fomiteDict = {f.id: f for f in fomites}
        self.tF = endtime
        self.t = 0
        self.contactNetwork=contactnetwork # people (1,2,3...) and fomites (1f, 2f, 3f,...)
        self.betaHH = param['contactRateHH']
        self.betaHF = param['contactRateHF']
        self.pickupFr = param['pickupFr']
        self.transferFr = param['transferFr']
        self.faceTouchRate = param['faceTouchRate']
        self.infProb = param['infProb']
        self.washRate = param['washRate']
        self.incubationRate = param['incubationRate']
        self.recoveryRate = param['recoveryRate']
        self.sheddingRate = param['sheddingRate']
        self.shedding = param['shedding']
        self.dieOff = param['dieOff']
        self.deconFreq = param['deconFreq']
        self.dayLength = param['dayLength']

        ### Initialize event dictionary
        self.events = {
            'human contact': 0,
            'infection': 0,
            'recovery': 0,
            'shedding': 0,
            'hand washing': 0,
            'fomite contact': 0
        }

        self.susceptibleAgents = []
        self.contaminatedAgents = []
        self.incubatingAgents = []
        self.infectedAgents = []
        self.output = []


        ### Filter agents by disease state
        self.populate_agent_lists(agents)

        ### Calculate initial event rates
        self.contactPairs = self.init_contact_pairs()
        self.fomitePairs = self.init_fomite_pairs()
        #print self.contactPairs.edges()
        #print self.contactPairs.nodes()
        # Susceptibles and contaminated neighbors may interact
        self.events['human contact'] = self.betaHH*self.contactPairs.size()
        # Contaminated agents self-innoculate
        self.events['infection'] = self.faceTouchRate*len(self.contaminatedAgents)
        # All agents wash hands, but no need to count susceptibles
        self.events['hand washing'] = self.washRate*(self.N-len(self.susceptibleAgents))
        # Actively infectious agents can shed pathogen
        self.events['shedding'] = self.sheddingRate*len(self.infectedAgents)
        # Infectious agents can recover
        self.events['recovery'] = len(self.infectedAgents)*self.recoveryRate
        # Agents can contact fomites
        self.events['fomite contact'] = self.betaHF*self.fomitePairs.size()
        # Incubating agents develop symptoms
        self.events['symptom presentation'] = self.incubationRate*len(self.incubatingAgents)
        self.totalRate = np.sum(self.events.values())

    def run(self):
        for t in xrange(self.tF):
            #print 'day', t, len(self.infectedAgents), 'infected'
            self.output.append([len(self.susceptibleAgents),len(self.contaminatedAgents),len(self.incubatingAgents),len(self.infectedAgents),sum([self.fomiteDict[i].contamination for i in self.fomiteDict]), t])
            print t
            if self.deconFreq is not None:
                if not t%self.deconFreq:
                    for fId in self.fomiteDict:
                        self.fomiteDict[fId].comtamination = 0
            #print self.events
            h = 0
            for i in self.agentDict:
                a = self.agentDict[i]
                a.timestamp = h
                if a.contamination == 0 and a.state == 1:
                    a.state = 0
                    self.update_contact_pairs(i)

            for j in self.fomiteDict:
                self.fomiteDict[j].timestamp = h
            #print self.contactPairs.edges()
            while h < self.dayLength:
                #print h

                if self.totalRate > 0:
                    dh = self.draw_event_time()
                    #print dh
                    if dh < self.dayLength - h:
                        event = self.draw_event()
                        #print self.events
                        self.resolve(event)
                        self.update_event_rates()
                        h += dh
                        self.t += dh
                    else:
                        break
                else:
                    break

            #fix this later for multiple fomites
            #self.output[t][4] = self.fomite.contamination

            ## agents wash at the end of the day
            '''
            for i in self.agentDict:
                if self.agentDict[i].state == 1:
                    self.agentDict[i].state = 0
                self.agentDict[i].contamination = 0
            self.susceptibleAgents += self.contaminatedAgents
            self.contaminatedAgents = []
            self.update_event_rates()
            '''

            #print 'fomite contamination', self.fomite.contamination

            ## fomite is decontaminated at the end of the day
            #for j in self.fomiteDict:
            #    self.fomiteDict[j].contamination = 0

    def draw_event_time(self):
        return np.random.exponential(scale=1/float(self.totalRate))

    def draw_event(self):
        r = np.random.random()
        s = 0.0
        for event, rate in self.events.iteritems():
            s += rate/float(self.totalRate)
            if r < s:
                return event
        return event

    def contact(self):
        pair = pr.choice(self.contactPairs.edges())
        #print '  contact between', pair

        i = pair[0]
        j = pair[1]

        self.transfer_contamination(i,j)

        self.agentDict[i].timestamp = self.t
        self.agentDict[j].timestamp = self.t

    def infect(self):
        #print self.contaminatedAgents
        i = pr.choice(self.contaminatedAgents)
        a = self.agentDict[i]
        #print ' ', i, 'consumed pathogen'
        a.pathogen_decay(self.t,self.dieOff)
        a.timestamp = self.t
        if np.random.random() < a.contamination*self.infProb:
            print ' ', i, 'became infected'
            #print ' ', a.contamination*self.infProb
            a = self.agentDict[i]
            a.state = 2
            self.contaminatedAgents.remove(i)
            self.incubatingAgents.append(i)

    def recover(self):
        i = pr.choice(self.infectedAgents)
        print ' ', i, 'recovered'
        #print self.contactPairs.nodes()
        self.agentDict[i].state = 4
        #self.agentDict[i].contamination = 0
        self.infectedAgents.remove(i)
        nBors = self.contactPairs.edges(i)
        self.contactPairs.remove_edges_from(nBors)

    def shed(self):
        i = pr.choice(self.infectedAgents)
        #print ' ', i, 'sheds'
        a = self.agentDict[i]
        a.pathogen_decay(self.t,self.dieOff)
        a.timestamp = self.t
        a.contamination += self.shedding
        #print a.fomiteNeighbors
        j = pr.choice(a.fomiteNeighbors)
        #print j
        self.fomiteDict[j].pathogen_decay(self.t,self.dieOff)
        self.fomiteDict[j].contamination += self.shedding

    def wash(self):
        i = pr.choice(tuple(set(self.agentDict.keys()).difference(set(self.susceptibleAgents))))
        #print set(self.agentDict.keys()).difference(set(self.susceptibleAgents))
        #print ' ', i, 'washed their hands'
        a = self.agentDict[i]
        if a.state == 1:
            a.state = 0
            self.contaminatedAgents.remove(i)
            self.susceptibleAgents.append(i)
            self.update_contact_pairs(i)
        a.contamination = 0


    def touch(self):
        i = pr.choice(self.agentDict.keys())
        a = self.agentDict[i]
        #print ' ', i, 'touched a fomite'
        j = pr.choice(a.fomiteNeighbors)
        f = self.fomiteDict[j]
        if a.state == 0 and f.contamination > 0:
            a.state = 1
            self.susceptibleAgents.remove(i)
            self.contaminatedAgents.append(i)
            self.update_contact_pairs(i)
        a.pathogen_decay(self.t,self.dieOff)
        f.pathogen_decay(self.t,self.dieOff)
        pickup = f.contamination*self.pickupFr
        a.contamination += pickup
        f.contamination -= pickup
        a.timestamp = self.t
        f.timestamp = self.t

    def present(self):
        i = pr.choice(self.incubatingAgents)
        print ' ', i, 'developed symptoms'
        a = self.agentDict[i]
        a.state == 3
        self.incubatingAgents.remove(i)
        self.infectedAgents.append(i)
        newPairs = [(i,j) for j in a.neighbors if self.agentDict[j].state in (0,1)]
        self.contactPairs.add_edges_from(newPairs)

    def transfer_contamination(self,i,j):
        a = self.agentDict[i]
        b = self.agentDict[j]

        a.pathogen_decay(self.t,self.dieOff)
        b.pathogen_decay(self.t,self.dieOff)

        cA = a.contamination
        cB = b.contamination

        a.contamination = cA + self.transferFr*cB - self.transferFr*cA
        b.contamination = cB + self.transferFr*cA - self.transferFr*cB


        #print a.contamination, b.contamination
        if a.contamination > 0:
            if a.state == 0:
                a.state = 1
            self.update_contact_pairs(i)
        if b.contamination > 0:
            if b.state == 0:
                b.state = 1
            self.update_contact_pairs(j)

    def init_contact_pairs(self):
        ## Tell each agent who their neighbors are
        for id in self.agentDict:
            #print self.contactNetwork.neighbors(id)
            self.agentDict[id].neighbors = [n for n in self.contactNetwork.neighbors(id) if nx.get_node_attributes(self.contactNetwork,'bipartite')[n] == 1]
            #print self.agentDict[id].neighbors
        ## Create the transmission subgraph
        pairs = nx.Graph()
        for i in self.susceptibleAgents:
            a = self.agentDict[i]
            for j in a.neighbors:
                b = self.agentDict[j]
                if b.state != 0:
                    pairs.add_edge(i,j)
        return pairs

    def init_fomite_pairs(self):
        ## Tell each fomite who its neighbors are
        # might not need to store this, check later
        for id in self.fomiteDict:
            self.fomiteDict[id].neighbors = [n for n in self.contactNetwork.neighbors(id) if nx.get_node_attributes(self.contactNetwork,'bipartite')[n] == 1]

        ## Tell each person which fomites they touch
        for id in self.agentDict:
            self.agentDict[id].fomiteNeighbors = [n for n in self.contactNetwork.neighbors(id) if nx.get_node_attributes(self.contactNetwork,'bipartite')[n] == 0]

        ## Create the human-fomite subgraph
        pairs = nx.Graph()
        for i in self.fomiteDict:
            f = self.fomiteDict[i]
            for j in f.neighbors:
                pairs.add_edge(i,j)
        return pairs

    def update_contact_pairs(self,i):
        ### Change the contact pair graph after an agent changes state
        #print self.t
        #print self.contactPairs.edges()
        a = self.agentDict[i]
        for j in a.neighbors:
            b = self.agentDict[j]
            #print 'i', i, 'j', j
            #print 'state A', a.state, 'state B', b.state
            if b.state == 0:
                if a.state == 0:
                    self.contactPairs.remove_edge(i,j)
                else:
                    self.contactPairs.add_edge(i,j)


    def populate_agent_lists(self,aList):
        for a in aList:
            if a.state == 0:
                self.susceptibleAgents.append(a.id)
            elif a.state == 1:
                self.contaminatedAgents.append(a.id)
            elif a.state == 2:
                self.incubatingAgents.append(a.id)
            elif a.state == 3:
                self.infectedAgents.append(a.id)

    def update_event_rates(self):
        # Susceptibles and contaminated neighbors may interact
        self.events['human contact'] = self.betaHH*self.contactPairs.size()
        # Contaminated agents self-innoculate
        self.events['infection'] = self.faceTouchRate*len(self.contaminatedAgents)
        # All agents wash hands, but no need to count susceptibles
        self.events['hand washing'] = self.washRate*(self.N-len(self.susceptibleAgents))
        # Actively infectious agents can shed pathogen
        self.events['shedding'] = self.sheddingRate*len(self.infectedAgents)
        # Infectious agents can recover
        self.events['recovery'] = len(self.infectedAgents)*self.recoveryRate
        # Agents can contact fomite
        self.events['fomite contact'] = self.betaHF*self.fomitePairs.size()
        # Incubating agents develop symptoms
        self.events['symptom presentation'] = self.incubationRate*len(self.incubatingAgents)
        self.totalRate = np.sum(self.events.values())

    def resolve(self,event):
        dispatch = {
            'human contact': self.contact,
            'infection': self.infect,
            'recovery': self.recover,
            'shedding': self.shed,
            'hand washing': self.wash,
            'fomite contact': self.touch,
            'symptom presentation': self.present
        }
        dispatch[event]()

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root, top, mod
    global parameters
    mod = 0
    parameters = {'contactRateHH':0.0, 'contactRateHF':0.0, 'pickupFr':0.0, 'transferFr':0.0, 'faceTouchRate':0.0, 'infProb':0.0, 'washRate':0.0, 'incubationRate':0.0, 'recoveryRate':0.0, 'sheddingRate':0.0, 'shedding':0.0, 'dieOff':0.0, 'deconFreq':None, 'dayLength':0.0}
    root = Tk()
    top = New_Toplevel_1 (root)
    root.protocol('WM_DELETE_WINDOW',lambda: close())
    dummy1 = open('fig1.png', 'w')
    dummy2 = open('fig2.png', 'w')
    root.resizable(width=False, height=False)
    root.mainloop()

def close():
    #check for extraneous/duplicates
    os.remove('fig1.png')
    os.remove('fig2.png')
    root.destroy()

class New_Toplevel_1:
    def __init__(self, top=None):
        '''This class configures and populates the toplevel window.
           top is the toplevel containing window.'''
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#d9d9d9' # X11 color: 'gray85'
        _ana1color = '#d9d9d9' # X11 color: 'gray85'
        _ana2color = '#d9d9d9' # X11 color: 'gray85'
        font10 = "-family {DejaVu Sans Mono} -size 15 -weight normal "  \
            "-slant roman -underline 0 -overstrike 1"
        font11 = "-family {DejaVu Sans Mono} -size 15 -weight bold "  \
            "-slant roman -underline 0 -overstrike 0"
        font9 = "-family {DejaVu Sans Mono} -size 15 -weight normal "  \
            "-slant roman -underline 0 -overstrike 0"

        global days, agents
        days = 10
        agents = 20
        top.geometry("1031x593+89+80")
        top.title('Maize & Blue SIWR v2.0')
        top.configure(background="#135bd9")
        top.configure(highlightcolor="black")
        top.configure(cursor='pencil')

        self.Label1 = Label(top)
        self.Label1.place(relx=0.01, rely=0.03, height=18, width=126)
        self.Label1.configure(activebackground="#135bd9")
        self.Label1.configure(activeforeground="white")
        self.Label1.configure(background="#135bd9")
        self.Label1.configure(text='''Contact Rate HH''')

        self.Label15 = Label(top)
        self.Label15.place(relx=0.03, rely=0.07, height=18, width=126)
        self.Label15.configure(activebackground="#f9f9f9")
        self.Label15.configure(background="#135bd9")
        self.Label15.configure(text='''Contact Rate HF''')

        self.Label14 = Label(top)
        self.Label14.place(relx=-.01, rely=0.11, height=18, width=126)
        self.Label14.configure(activebackground="#f9f9f9")
        self.Label14.configure(background="#135bd9")
        self.Label14.configure(text='''Pickup FR''')

        self.Label5 = Label(top)
        self.Label5.place(relx=0.015, rely=0.15, height=18, width=126)
        self.Label5.configure(activebackground="#f9f9f9")
        self.Label5.configure(background="#135bd9")
        self.Label5.configure(text='''Transfer FR''')

        self.Label4 = Label(top)
        self.Label4.place(relx=0.01, rely=0.19, height=18, width=126)
        self.Label4.configure(activebackground="#f9f9f9")
        self.Label4.configure(background="#135bd9")
        self.Label4.configure(text='''Face Touch Rate''')

        self.Label6 = Label(top)
        self.Label6.place(relx=0.008, rely=0.23, height=18, width=126)
        self.Label6.configure(activebackground="#f9f9f9")
        self.Label6.configure(background="#135bd9")
        self.Label6.configure(text='''INF Prob''')

        self.Label7 = Label(top)
        self.Label7.place(relx=-.01, rely=0.27, height=18, width=126)
        self.Label7.configure(activebackground="#f9f9f9")
        self.Label7.configure(background="#135bd9")
        self.Label7.configure(text='''Wash Rate''')

        self.Label8 = Label(top)
        self.Label8.place(relx=0.03, rely=0.31, height=18, width=126)
        self.Label8.configure(activebackground="#f9f9f9")
        self.Label8.configure(background="#135bd9")
        self.Label8.configure(text='''Incubation Rate''')

        self.Label9 = Label(top)
        self.Label9.place(relx=0.003, rely=0.35, height=18, width=126)
        self.Label9.configure(activebackground="#f9f9f9")
        self.Label9.configure(background="#135bd9")
        self.Label9.configure(text='''Recovery Rate''')

        self.Label10 = Label(top)
        self.Label10.place(relx=0.027, rely=0.39, height=18, width=126)
        self.Label10.configure(activebackground="#f9f9f9")
        self.Label10.configure(background="#135bd9")
        self.Label10.configure(text='''Shedding Rate''')

        self.Label11 = Label(top)
        self.Label11.place(relx=-.01, rely=0.43, height=18, width=126)
        self.Label11.configure(activebackground="#f9f9f9")
        self.Label11.configure(background="#135bd9")
        self.Label11.configure(text='''Shedding''')

        self.Label12 = Label(top)
        self.Label12.place(relx=0.00, rely=0.47, height=18, width=126)
        self.Label12.configure(activebackground="#f9f9f9")
        self.Label12.configure(background="#135bd9")
        self.Label12.configure(text='''Dieoff''')

        self.Label3 = Label(top)
        self.Label3.place(relx=-.003, rely=0.51, height=18, width=126)
        self.Label3.configure(activebackground="#f9f9f9")
        self.Label3.configure(background="#135bd9")
        self.Label3.configure(text='''Decon Freq''')

        self.Label13 = Label(top)
        self.Label13.place(relx=0.018, rely=0.55, height=18, width=126)
        self.Label13.configure(activebackground="#f9f9f9")
        self.Label13.configure(background="#135bd9")
        self.Label13.configure(text='''Day Length''')

        self.Entry1 = Entry(top)
        self.Entry1.place(relx=0.17, rely=0.03, relheight=0.03, relwidth=0.14)
        self.Entry1.configure(background="white")
        self.Entry1.configure(font="TkFixedFont")
        self.Entry1.configure(selectbackground="#c4c4c4")

        self.Entry2 = Entry(top)
        self.Entry2.place(relx=0.19, rely=0.07, relheight=0.03, relwidth=0.14)
        self.Entry2.configure(background="white")
        self.Entry2.configure(font="TkFixedFont")
        self.Entry2.configure(selectbackground="#c4c4c4")

        self.Entry3 = Entry(top)
        self.Entry3.place(relx=0.17, rely=0.11, relheight=0.03, relwidth=0.14)
        self.Entry3.configure(background="white")
        self.Entry3.configure(font="TkFixedFont")
        self.Entry3.configure(selectbackground="#c4c4c4")

        self.Entry4 = Entry(top)
        self.Entry4.place(relx=0.19, rely=0.15, relheight=0.03, relwidth=0.14)
        self.Entry4.configure(background="white")
        self.Entry4.configure(font="TkFixedFont")
        self.Entry4.configure(selectbackground="#c4c4c4")

        self.Entry5 = Entry(top)
        self.Entry5.place(relx=0.17, rely=0.19, relheight=0.03, relwidth=0.14)
        self.Entry5.configure(background="white")
        self.Entry5.configure(font="TkFixedFont")
        self.Entry5.configure(selectbackground="#c4c4c4")

        self.Entry6 = Entry(top)
        self.Entry6.place(relx=0.19, rely=0.23, relheight=0.03, relwidth=0.14)
        self.Entry6.configure(background="white")
        self.Entry6.configure(font="TkFixedFont")
        self.Entry6.configure(selectbackground="#c4c4c4")

        self.Entry7 = Entry(top)
        self.Entry7.place(relx=0.17, rely=0.27, relheight=0.03, relwidth=0.14)
        self.Entry7.configure(background="white")
        self.Entry7.configure(font="TkFixedFont")
        self.Entry7.configure(selectbackground="#c4c4c4")

        self.Entry8 = Entry(top)
        self.Entry8.place(relx=0.19, rely=0.31, relheight=0.03, relwidth=0.14)
        self.Entry8.configure(background="white")
        self.Entry8.configure(font="TkFixedFont")
        self.Entry8.configure(selectbackground="#c4c4c4")

        self.Entry9 = Entry(top)
        self.Entry9.place(relx=0.17, rely=0.35, relheight=0.03, relwidth=0.14)
        self.Entry9.configure(background="white")
        self.Entry9.configure(font="TkFixedFont")
        self.Entry9.configure(selectbackground="#c4c4c4")

        self.Entry10 = Entry(top)
        self.Entry10.place(relx=0.19, rely=0.39, relheight=0.03, relwidth=0.14)
        self.Entry10.configure(background="white")
        self.Entry10.configure(font="TkFixedFont")
        self.Entry10.configure(selectbackground="#c4c4c4")

        self.Entry11 = Entry(top)
        self.Entry11.place(relx=0.17, rely=0.43, relheight=0.03, relwidth=0.14)
        self.Entry11.configure(background="white")
        self.Entry11.configure(font="TkFixedFont")
        self.Entry11.configure(selectbackground="#c4c4c4")

        self.Entry12 = Entry(top)
        self.Entry12.place(relx=0.19, rely=0.47, relheight=0.03, relwidth=0.14)
        self.Entry12.configure(background="white")
        self.Entry12.configure(font="TkFixedFont")
        self.Entry12.configure(selectbackground="#c4c4c4")

        self.Entry13 = Entry(top)
        self.Entry13.place(relx=0.17, rely=0.51, relheight=0.03, relwidth=0.14)
        self.Entry13.configure(background="white")
        self.Entry13.configure(font="TkFixedFont")
        self.Entry13.configure(selectbackground="#c4c4c4")

        self.Entry14 = Entry(top)
        self.Entry14.place(relx=0.19, rely=0.55, relheight=0.03, relwidth=0.14)
        self.Entry14.configure(background="white")
        self.Entry14.configure(font="TkFixedFont")
        self.Entry14.configure(selectbackground="#c4c4c4")

        self.Button1 = Button(top)
        self.Button1.place(relx=0.02, rely=0.65, height=26, width=157)
        self.Button1.configure(activebackground="#d9d9d9")
        self.Button1.configure(background="#d9d938")
        self.Button1.configure(font=font9)
        self.Button1.configure(text='''Save''')
        self.Button1.configure(cursor='crosshair')
        self.Button1.configure(command=lambda: but1Press())

        self.Button2 = Button(top)
        self.Button2.place(relx=0.18, rely=0.65, height=26, width=157)
        self.Button2.configure(activebackground="#d9d9d9")
        self.Button2.configure(background="#d9d938")
        self.Button2.configure(font=font9)
        self.Button2.configure(text='''Load''')
        self.Button2.configure(cursor='crosshair')
        self.Button2.configure(command=lambda: but2Press())

        self.Button3 = Button(top)
        self.Button3.place(relx=0.02, rely=0.71, height=26, width=157)
        self.Button3.configure(activebackground="#d9d9d9")
        self.Button3.configure(background="#d9d938")
        self.Button3.configure(font=font11)
        self.Button3.configure(text='''Generate''')
        self.Button3.configure(cursor='crosshair')
        self.Button3.configure(command=lambda: but3Press())

        self.Button4 = Button(top)
        self.Button4.place(relx=0.18, rely=0.71, height=26, width=157)
        self.Button4.configure(activebackground="#d9d9d9")
        self.Button4.configure(background="#d9d938")
        self.Button4.configure(font=font10)
        self.Button4.configure(text='''Clear''')
        self.Button4.configure(cursor='crosshair')
        self.Button4.configure(command=lambda: but4Press())

        self.Label2 = Label(top)
        self.Label2.place(relx=0.4, rely=0.03, height=18, width=33)
        self.Label2.configure(activebackground="#f9f9f9")
        self.Label2.configure(background="#135bd9")
        self.Label2.configure(text='''Days''')

        self.Entry15 = Entry(top)
        self.Entry15.place(relx=0.44, rely=0.03, relheight=0.03, relwidth=0.14)
        self.Entry15.configure(background="white")
        self.Entry15.configure(font="TkFixedFont")
        self.Entry15.configure(selectbackground="#c4c4c4")
        self.Entry15.insert(0,days)

        self.Label16 = Label(top)
        self.Label16.place(relx=0.6, rely=0.03, height=18, width=51)
        self.Label16.configure(activebackground="#f9f9f9")
        self.Label16.configure(background="#135bd9")
        self.Label16.configure(text='''Agents''')

        self.Entry16 = Entry(top)
        self.Entry16.place(relx=0.656, rely=0.03, relheight=0.03, relwidth=0.14)
        self.Entry16.configure(background="white")
        self.Entry16.configure(font="TkFixedFont")
        self.Entry16.configure(selectbackground="#c4c4c4")
        self.Entry16.insert(0,agents)

        self.Button5 = Button(top)
        self.Button5.place(relx=0.4, rely=0.12, height=486, width=587)
        self.Button5.configure(activebackground="#d9d9d9")
        self.Button5.configure(state=ACTIVE)
        self.Button5.configure(cursor='exchange')
        self.Button5.configure(command=lambda: but5Press())

    def take(self):
        global days, agents
        self.entries = []
        self.entries.append(self.Entry1.get())
        self.entries.append(self.Entry2.get())
        self.entries.append(self.Entry3.get())
        self.entries.append(self.Entry4.get())
        self.entries.append(self.Entry5.get())
        self.entries.append(self.Entry6.get())
        self.entries.append(self.Entry7.get())
        self.entries.append(self.Entry8.get())
        self.entries.append(self.Entry9.get())
        self.entries.append(self.Entry10.get())
        self.entries.append(self.Entry11.get())
        self.entries.append(self.Entry12.get())
        self.entries.append(self.Entry13.get())
        self.entries.append(self.Entry14.get())
        days = int(self.Entry15.get())
        agents = int(self.Entry16.get())
    def give(self, vals=[]):
        print(vals)
        self.Entry1.insert(0,vals[0])
        self.Entry2.insert(0,vals[1])
        self.Entry3.insert(0,vals[2])
        self.Entry4.insert(0,vals[3])
        self.Entry5.insert(0,vals[4])
        self.Entry6.insert(0,vals[5])
        self.Entry7.insert(0,vals[6])
        self.Entry8.insert(0,vals[7])
        self.Entry9.insert(0,vals[8])
        self.Entry10.insert(0,vals[9])
        self.Entry11.insert(0,vals[10])
        self.Entry12.insert(0,vals[11])
        self.Entry13.insert(0,vals[12])
        self.Entry14.insert(0,vals[13])

def but1Press():
    dialog = tkSimpleDialog.askstring('SIWR Input', 'Input a file name:')
    dialog += '.siwr'
    out = open(dialog, 'w')
    top.take()
    for x in top.entries:
        out.write(x)
        out.write(' ')

def but2Press():
    name = tkFileDialog.askopenfilename()
    out = open(name, 'r')
    params = out.read().split()
    top.give(params)

def but3Press():
    try:
        global parameters
        top.take()
        parameters['contactRateHH'] = float(top.entries[0])
        parameters['contactRateHF'] = float(top.entries[1])
        parameters['pickupFr'] = float(top.entries[2])
        parameters['transferFr'] = float(top.entries[3])
        parameters['faceTouchRate'] = float(top.entries[4])
        parameters['infProb'] = float(top.entries[5])
        parameters['washRate'] = float(top.entries[6])
        parameters['incubationRate'] = float(top.entries[7])
        parameters['recoveryRate'] = float(top.entries[8])
        parameters['sheddingRate'] = float(top.entries[9])
        parameters['shedding'] = float(top.entries[10])
        parameters['dieOff'] = float(top.entries[11])
        if(float(top.entries[12]) != 0):
            parameters['deconFreq'] = float(top.entries[12])
        else:
            parameters['deconFreq'] = None
        parameters['dayLength'] = float(top.entries[13])
        gen()
    except:
        tkMessageBox.showwarning("Warning!","Unfilled Parameters!")

def but4Press():
    top.Entry1.delete(0,END)
    top.Entry2.delete(0,END)
    top.Entry3.delete(0,END)
    top.Entry4.delete(0,END)
    top.Entry5.delete(0,END)
    top.Entry6.delete(0,END)
    top.Entry7.delete(0,END)
    top.Entry8.delete(0,END)
    top.Entry9.delete(0,END)
    top.Entry10.delete(0,END)
    top.Entry11.delete(0,END)
    top.Entry12.delete(0,END)
    top.Entry13.delete(0,END)
    top.Entry14.delete(0,END)

def but5Press():
    global mod
    if mod == 1:
        top.Button5.configure(image=image2)
        mod = 2
    elif mod == 2:
        top.Button5.configure(image=image1)
        mod = 1

def gen():
    from fomite_ABM_GUI_v2 import Agent, Fomite

    ### A bunch of crap to test run the model
    agentList = []
    fomite = Fomite(id='1f')
    nAgents = agents
    for i in range(nAgents):
        agentList.append(Agent(id=i))
    agentList[1].state = 3
    #agentList[1].recoveryTime = 7
    agentList[1].contamination = 500
    ## This matrix assumes one fomite that everybody touches
    G = nx.complete_graph(nAgents)
    #print G.edges()
    nx.set_node_attributes(G,'bipartite',1)
    G.add_node(fomite.id,bipartite=0)

    for i in range(nAgents):
        G.add_edge(i,'1f')

    #print G.neighbors(1)
    #param = parameters.values()
    #print('param', len(param))
    print(parameters)
    print(days)
    print(agents)
    param = copy.deepcopy(parameters)
    #print globals()
    #reformatted parameters as dictionary for retrieval
    #GUI generation

    ### parallelized multiple runs
    '''
    servers = ('local',)
    jobServer = pp.Server(ppservers=servers)
    print 'active nodes', jobServer.get_active_nodes()
    mList = [Model(copy.deepcopy(agentList),[copy.deepcopy(fomite)],28,G,param) for i in range(200)]

    output = []
    start = time.time()
    jobs = [jobServer.submit(run_model,args=(m,),modules=('numpy as np','networkx as nx','random as pr')) for m in mList]
    for job in jobs:
        output.append(job())
    print 'time elapsed', time.time()-start

    output = np.array(output)
    avgOutput = np.mean(output,axis=0)
    stdOutput = np.std(output,axis=0)

    upperBound = avgOutput + stdOutput
    lowerBound = avgOutput - stdOutput
    days = avgOutput[:,-1]
    pl.plot(days,avgOutput[:,3],'b',lw=4,label='Symptomatic')
    pl.fill_between(days,lowerBound[:,3],upperBound[:,3],facecolor='b',lw=0,alpha=0.5)
    pl.plot(days,avgOutput[:,2],'g',lw=4,label='Incubating')
    pl.fill_between(days,lowerBound[:,2],upperBound[:,2],facecolor='g',lw=0,alpha=0.5)
    pl.legend(loc=0)
    pl.ylabel('Symptomatic')
    pl.xlabel('Days')
    pl.ylim(ymin=0)
    pl.figure()
    pl.plot(days,avgOutput[:,4],color='r',lw=4)
    pl.fill_between(days,lowerBound[:,4],upperBound[:,4],facecolor='r',lw=0,alpha=0.5)
    pl.ylabel('Fomite contamination')
    pl.xlabel('Days')
    pl.ylim(ymin=0)
    pl.show()
    '''

    m = Model(agentList,[fomite,],days,G,param)
    #print m.contactPairs.edges()

    m.run()

    out = np.array(m.output)
    #print out[:,2]

    pl.plot(out[:,-1],out[:,3],label='Symptomatic')
    pl.plot(out[:,-1],out[:,2],label='Incubating')
    pl.legend()
    pl.ylabel('Population')
    pl.xlabel('Days')
    pl.savefig('fig1')
    pl.plot(out[:,-1],out[:,4], label=None)
    pl.ylabel('Fomite contamination')
    pl.xlabel('Days')
    pl.legend().remove()
    pl.savefig('fig2')
    pl.clf()

    global image1
    global image2
    global mod

    mod = 1

    img = Image.open('fig1.png')
    img = img.resize((587,486), PIL.Image.ANTIALIAS)
    img.save('fig1.png')

    img = Image.open('fig2.png')
    img = img.resize((587,486), PIL.Image.ANTIALIAS)
    img.save('fig2.png')

    image1 = ImageTk.PhotoImage(file='fig1.png')
    image2 = ImageTk.PhotoImage(file='fig2.png')
    top.Button5.configure(image=image1)

    #print 'fomite contamination', m.fomite.contamination
    #for a in m.agentList:
    #    print 'state', a.state
    #    print 'contamination', a.contamination
    #for a in m.agentList:
    #    print a.neighbors

if __name__ == '__main__':
    vp_start_gui()
