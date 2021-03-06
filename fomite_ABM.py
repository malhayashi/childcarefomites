import numpy as np
import networkx as nx
import random as pr
import numpy.random as npr
import matplotlib.pyplot as pl
import datetime as dt
import pp
import time
import copy
import sys
import os
import matplotlib
from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
from math import *
from networkx.algorithms import bipartite

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

def run_model(m):
    m.run()
    return np.array(m.output)

def run_parallel(agentList, fomiteList, endDay, contactNetwork, param, nRuns):
    servers = ('local',)
    jobServer = pp.Server(ppservers=servers)
    jobServer.set_ncpus(jobServer.get_ncpus()-2)
    print 'active nodes', jobServer.get_active_nodes()
    mList = [Model(copy.deepcopy(agentList),copy.deepcopy(fomiteList),endDay,contactNetwork,param) for i in range(nRuns)]
    print 'submitting jobs'
    output = []
    start = time.time()
    jobs = [jobServer.submit(run_model,args=(m,),depfuncs=(timestamp_to_hours,),modules=('numpy as np','networkx as nx','random as pr','datetime as dt')) for m in mList]
    for job in jobs:
        output.append(job())
    print 'time elapsed', time.time()-start

    output = np.array(output)
    return output

def process_agent_data(agentDict):
    dataDict = {}
    for id in agentDict.keys():
        a = agentDict[id]
        for x in a.data:
            timestamp = x[0]
            state = x[1]
            if timestamp in dataDict.keys():
                dataDict[timestamp][state] += 1
            else:
                dataDict[timestamp] = [0,0,0,0,0]
                dataDict[timestamp][state] += 1
    print dataDict

def timestamp_to_hours(ts):
    return ts.total_seconds() / float(3600)

class Agent(object):
    def __init__(self, id, state=0, contamination=0, neighbors=[], recoverytime=dt.timedelta(),isinfectious=False):
        self.id = id
        self.state = state # 0: S, 1: C, 2: I1, 3: I2, 4: R
        self.contamination = contamination
        #self.day = 0
        self.timestamp = dt.timedelta()
        self.neighbors = neighbors
        self.fomiteNeighbors = []
        self.recoveryTime = recoverytime
        self.isInfectious = isinfectious
        self.data = [(self.timestamp,self.state),]

    def pathogen_decay(self,t,r):
        x = self.contamination*exp(-r*(t-timestamp_to_hours(self.timestamp)))
        self.contamination = max(x,0)

class Fomite(object):
    def __init__(self, id, contamination=0, neighbors=[], decon=None):
        self.id = id
        self.contamination = contamination
        self.timestamp = dt.timedelta()
        self.neighbors = neighbors
        self.decon = decon  # Allows arbitrary decontamination schedule functions

    def pathogen_decay(self,t,r):
        x = self.contamination*exp(-r*(t-timestamp_to_hours(self.timestamp)))
        self.contamination = max(x,0)

class Model(object):

    def __init__(self,agents,fomites,endtime,contactnetwork,param):
        self.agentDict = {a.id: a for a in agents}
        self.N = len(self.agentDict.keys())
        ### Initialize rate parameters
        self.fomiteDict = {f.id: f for f in fomites}
        self.tF = endtime
        self.timestamp = dt.timedelta()
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
            'fomite contact': 0,
            'symptom presentation': 0
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
            #print t
            if self.deconFreq is not None:
                if not t%self.deconFreq:
                    for fId in self.fomiteDict:
                        self.fomiteDict[fId].comtamination = 0
            #print self.events
            h = 0
            for i in self.agentDict:
                a = self.agentDict[i]
                a.timestamp = dt.timedelta(days = t,hours = h)
                if a.contamination == 0 and a.state == 1:
                    a.state = 0
                    self.susceptibleAgents.append(i)
                    self.update_contact_pairs(i)

            for j in self.fomiteDict:
                self.fomiteDict[j].timestamp = dt.timedelta(days = t,hours = h)
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
                        self.timestamp = dt.timedelta(days=t,hours=h)
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
        pair = pr.choice(list(self.contactPairs.edges))
        #print '  contact between', pair

        i = pair[0]
        j = pair[1]

        self.transfer_contamination(i,j)

        self.agentDict[i].timestamp = self.timestamp
        self.agentDict[j].timestamp = self.timestamp

    def infect(self):
        #print self.contaminatedAgents
        i = pr.choice(self.contaminatedAgents)
        a = self.agentDict[i]
        #print ' ', i, 'consumed pathogen'
        a.pathogen_decay(timestamp_to_hours(self.timestamp),self.dieOff)
        a.timestamp = self.timestamp
        if np.random.random() < a.contamination*self.infProb:
            #print ' ', i, 'became infected'
            #print ' ', a.contamination*self.infProb
            a = self.agentDict[i]
            a.state = 2
            a.data.append((self.timestamp, a.state))
            self.contaminatedAgents.remove(i)
            self.incubatingAgents.append(i)

    def recover(self):
        i = pr.choice(self.infectedAgents)
        #print ' ', i, 'recovered'
        #print self.contactPairs.nodes()
        a = self.agentDict[i]
        a.state = 4
        a.data.append((self.timestamp,a.state))
        #self.agentDict[i].contamination = 0
        self.infectedAgents.remove(i)
        if a.neighbors:
            nBors = self.contactPairs.edges(i)
            self.contactPairs.remove_edges_from(nBors)


    def shed(self):
        i = pr.choice(self.infectedAgents)
        #print ' ', i, 'sheds'
        a = self.agentDict[i]
        a.pathogen_decay(timestamp_to_hours(self.timestamp),self.dieOff)
        a.timestamp = self.timestamp
        a.contamination += self.shedding
        #print a.fomiteNeighbors
        j = pr.choice(a.fomiteNeighbors)
        #print j
        self.fomiteDict[j].pathogen_decay(timestamp_to_hours(self.timestamp),self.dieOff)
        self.fomiteDict[j].contamination += self.shedding

    def wash(self):
        i = pr.choice(tuple(set(self.agentDict.keys()).difference(set(self.susceptibleAgents))))
        #print set(self.agentDict.keys()).difference(set(self.susceptibleAgents))
        #print ' ', i, 'washed their hands'
        a = self.agentDict[i]
        if a.state == 1:
            a.state = 0
            a.data.append((self.timestamp,a.state))
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
            a.data.append((self.timestamp,a.state))
            self.susceptibleAgents.remove(i)
            self.contaminatedAgents.append(i)
            self.update_contact_pairs(i)
        t = timestamp_to_hours(self.timestamp)
        a.pathogen_decay(t,self.dieOff)
        f.pathogen_decay(t,self.dieOff)
        pickup = f.contamination*self.pickupFr
        a.contamination += pickup
        f.contamination -= pickup
        a.timestamp = self.timestamp
        f.timestamp = self.timestamp

    def present(self):
        i = pr.choice(self.incubatingAgents)
        #print ' ', i, 'developed symptoms'
        a = self.agentDict[i]
        a.state = 3
        a.data.append((self.timestamp,a.state))
        self.incubatingAgents.remove(i)
        self.infectedAgents.append(i)
        newPairs = [(i,j) for j in a.neighbors if self.agentDict[j].state in (0,1)]
        self.contactPairs.add_edges_from(newPairs)

    def transfer_contamination(self,i,j):
        a = self.agentDict[i]
        b = self.agentDict[j]
        t = timestamp_to_hours(self.timestamp)
        a.pathogen_decay(t,self.dieOff)
        b.pathogen_decay(t,self.dieOff)

        cA = a.contamination
        cB = b.contamination

        a.contamination = cA + self.transferFr*cB - self.transferFr*cA
        b.contamination = cB + self.transferFr*cA - self.transferFr*cB


        #print a.contamination, b.contamination
        if a.contamination > 0:
            if a.state == 0:
                a.state = 1
                a.data.append((self.timestamp,a.state))
            self.update_contact_pairs(i)
        if b.contamination > 0:
            if b.state == 0:
                b.state = 1
                b.data.append((self.timestamp,b.state))
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

        ## Tell each person which fomites they toucht
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

    def compile_output(self):
        out = {}
        for i in self.agentDict.keys():
            a = self.agentDict[i]
            for entry in a.data:
                outRow = [0,0,0,0,0]
                
                time = entry[0].total_seconds()/float(3600*24)
                if time in out.keys():
                    out[time][entry[1]] += 1
                else:
                    outRow[entry[1]] = 1
                    out[time] = outRow
            
        self.output = [[k,]+out[k] for k in sorted(out)]
        
if __name__ == '__main__':
    from fomite_ABM import Agent, Fomite

    ### A bunch of crap to test run the model
    agentList = []
    fomite = Fomite(id='1f')
    fomite2 = Fomite(id='2f')
    nAgents = 30
    dayLength = 8
    for i in range(nAgents):
        agentList.append(Agent(id=i))
    agentList[1].state = 3
    agentList[1].data[0] = (dt.timedelta(),3)
    #agentList[1].recoveryTime = 7
    agentList[1].contamination = 500
    ## This matrix assumes one fomite that everybody touches
    print 'Building agent graph'
    #G = nx.complete_graph(nAgents)
    #G = nx.barabasi_albert_graph(nAgents,2)
    G = nx.erdos_renyi_graph(nAgents,0.04)
    #nx.draw(G)
    print 'avg degree', G.size()/float(G.number_of_nodes())
    #print G.edges()
    nx.set_node_attributes(G,values=1,name='bipartite')
    G.add_node(fomite.id,bipartite=0)
    G.add_node(fomite2.id,bipartite=0)
    print 'Building fomite graph'
    for i in range(nAgents):
        G.add_edge(i,'1f')
        if pr.random() < 0.3:
            G.add_edge(i,'2f')
    #print G.neighbors(1)
    param = {'contactRateHH':2/float(dayLength),
    'contactRateHF':10/float(dayLength),
    'pickupFr':0.1,
    'transferFr':0.25,
    'faceTouchRate':5,
    'infProb':0.0001,
    'washRate':1/float(dayLength),
    'incubationRate':1/float(2*dayLength),
    'recoveryRate':1/float(4*dayLength),
    'sheddingRate':5,
    'shedding':1000,
    'dieOff':2.8/float(dayLength),
    'deconFreq':1,
    'dayLength':8}

    output = run_parallel(agentList, [fomite,fomite2], 21, G, param, 100)
    #m = Model(agentList,[fomite,fomite2],14,G,param)
    #m.run()
    color = nx.get_node_attributes(G,'bipartite')

    nx.draw(G,node_color=[color[n] for n in G.nodes])
    #process_agent_data(m.agentDict)
    #print globals()

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
    '''
    #output = np.array(output)

    avgOutput = np.mean(output,axis=0)
    stdOutput = np.std(output,axis=0)

    upperBound = avgOutput + stdOutput
    lowerBound = avgOutput - stdOutput
    days = avgOutput[:,-1]

    font = {'family' : 'normal',
        'size'   : 18}

    matplotlib.rc('font', **font)

    pl.figure()
    pl.plot(days,avgOutput[:,3],'b',lw=4,label='Infectious')
    pl.fill_between(days,lowerBound[:,3],upperBound[:,3],facecolor='b',lw=0,alpha=0.5)
    pl.plot(days,avgOutput[:,2],'g',lw=4,label='Latent')
    pl.fill_between(days,lowerBound[:,2],upperBound[:,2],facecolor='g',lw=0,alpha=0.5)
    pl.legend(loc=0)
    pl.ylabel('Incidence')
    pl.xlabel('Days')
    pl.title('Simulated Child-Care Center\nGI Outbreak')
    pl.ylim(ymin=0)

    pl.tight_layout()
    #pl.savefig('example_simulations.png',dpi=300)

    pl.figure()
    pl.plot(days,avgOutput[:,4],color='r',lw=4)
    pl.fill_between(days,lowerBound[:,4],upperBound[:,4],facecolor='r',lw=0,alpha=0.5)
    pl.ylabel('Fomite contamination')
    pl.xlabel('Days')
    pl.ylim(ymin=0)
    pl.tight_layout()
    pl.show()


    #days = 14
    #m = Model(agentList,[fomite,],days,G,copy.deepcopy(param))
    #print m.contactPairs.edges()

    #m.run()

    #out = np.array(m.output)
    #print out[:,2]
    #pl.plot(out[:,-1],out[:,3],label='Symptomatic')
    #pl.plot(out[:,-1],out[:,2],label='Incubating')
    #pl.legend()
    #pl.ylabel('Population')
    #pl.xlabel('Days')
    #pl.figure()
    #pl.plot(out[:,-1],out[:,4])
    #pl.ylabel('Fomite contamination')
    #pl.xlabel('Days')
    #pl.show()

    #print 'fomite contamination', m.fomite.contamination
    #for a in m.agentList:
    #    print 'state', a.state
    #    print 'contamination', a.contamination
    #for a in m.agentList:
    #    print a.neighbors
