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
from fomite_ABM import *
from math import *
from PIL import Image
from PIL import ImageTk

global image1
global image2

def vp_start_gui():
    '''Starting point when module is the main routine.'''
    global val, w, root, top, mod, dummy1, dummy2, dummy3, dummy4
    global parameters
    mod = 0
    parameters = {'contactRateHH':0.0, 'contactRateHF':0.0, 'pickupFr':0.0, 'transferFr':0.0, 'faceTouchRate':0.0, 'infProb':0.0, 'washRate':0.0, 'incubationRate':0.0, 'recoveryRate':0.0, 'sheddingRate':0.0, 'shedding':0.0, 'dieOff':0.0, 'deconFreq':None, 'dayLength':0.0}
    root = Tk()
    top = New_Toplevel_1 (root)
    root.protocol('WM_DELETE_WINDOW',lambda: close())
    dummy1 = open('fig1.png', 'w')
    dummy2 = open('fig2.png', 'w')
    dummy3 = open('fig3.png', 'w')
    dummy4 = open('fig4.png', 'w')
    root.resizable(width=False, height=False)
    root.mainloop()

def close():
    #check for extraneous/duplicates
    dummy1.close()
    dummy2.close()
    dummy3.close()
    dummy4.close()
    os.remove('fig1.png')
    os.remove('fig2.png')
    os.remove('fig3.png')
    os.remove('fig4.png')
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
        top.title('Maize & Blue SIWR v2.11')
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

        self.Button6 = Button(top)
        self.Button6.place(relx=0.02, rely=0.80, height=26, width=322)
        self.Button6.configure(activebackground="#d9d9d9")
        self.Button6.configure(background="#d9d938")
        self.Button6.configure(font=font9)
        self.Button6.configure(text='''Economic Analysis''')
        self.Button6.configure(cursor='crosshair')
        self.Button6.configure(command=lambda: but6Press())

        self.Button7 = Button(top)
        self.Button7.place(relx=0.02, rely=0.86, height=26, width=322)
        self.Button7.configure(activebackground="#d9d9d9")
        self.Button7.configure(background="#d9d938")
        self.Button7.configure(font=font9)
        self.Button7.configure(text='''Curve Interpolation''')
        self.Button7.configure(cursor='crosshair')
        self.Button7.configure(command=lambda: but7Press())

        self.Button8 = Button(top)
        self.Button8.place(relx=0.02, rely=0.92, height=26, width=322)
        self.Button8.configure(activebackground="#d9d9d9")
        self.Button8.configure(background="#d9d938")
        self.Button8.configure(font=font9)
        self.Button8.configure(text='''Oppa Gangnam Style''')
        self.Button8.configure(cursor='crosshair')
        self.Button8.configure(command=lambda: but8Press())

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

    def _set_out(self, val, agents):
        self._total = val
        self._agents = agents

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
    '''except:
        tkMessageBox.showwarning("Warning!","Unfilled Parameters!")'''

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

def but6Press():
    from fomite_ABM_econGUI import vp_start_econgui
    vp_start_econgui(top)

def but7Press():
    #polynomial interpolation lagrange
    from Numericals import lagrange_interpolation
    from matplotlib.pylab import arange
    try:
        discretization_range = arange(0,days-1,.01)
        incubating_out = []
        symptomatic_out = []
        xvals = [x[-1] for x in complete_output]
        inyvals = [x[2] for x in complete_output]
        symyvals = [x[3] for x in complete_output]
        conyvals = [x[4] for x in complete_output]
        incubating_out = lagrange_interpolation(discretization_range, xvals, inyvals)
        symptomatic_out = lagrange_interpolation(discretization_range, xvals, symyvals)
        contamination_out = lagrange_interpolation(discretization_range, xvals, conyvals)

        print(xvals)
        print(incubating_out)
        global image1, image2, mod
        pl.clf()

        pl.plot(discretization_range,symptomatic_out,label='Symptomatic')
        pl.plot(discretization_range,incubating_out,label='Incubating')
        pl.legend()
        pl.ylabel('Population')
        pl.xlabel('Days')
        pl.savefig('fig1')
        pl.plot(discretization_range,contamination_out, label=None)
        pl.ylabel('Fomite contamination')
        pl.xlabel('Days')
        pl.legend().remove()
        pl.savefig('fig2')
        pl.clf()

        img = Image.open('fig1.png')
        img = img.resize((587,486), PIL.Image.ANTIALIAS)
        img.save('fig1.png')

        img = Image.open('fig2.png')
        img = img.resize((587,486), PIL.Image.ANTIALIAS)
        img.save('fig2.png')

        image1 = ImageTk.PhotoImage(file='fig1.png')
        image2 = ImageTk.PhotoImage(file='fig2.png')
        mod = 1

        top.Button5.configure(image=image1)
    except:
        tkMessageBox.showwarning("Warning!","No Curve to Interpolate!")

def but8Press():
    print('gangnam style')
    #retrieve TSV and integrate to model
    name = tkFileDialog.askopenfilename()
    from sickchildcare_parser import cases_to_agents
    agents = cases_to_agents(name, 'all', 'e', 5)
    print(agents)
    for i in agents:
        print(i.data)

def gen():
    from fomite_ABM import Agent, Fomite

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

    global complete_output
    complete_output = m.output
    #safe copy by value NOT reference
    top._set_out(complete_output, agentList)
    out = np.array(complete_output)
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
