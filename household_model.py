import numpy as np
import networkx as nx
import random as pr
import matplotlib.pyplot as pl
import datetime as dt
import pp
import time
import copy
import sys
import os
from Tkinter import *
import tkFileDialog
import tkSimpleDialog
import tkMessageBox
from math import *
from fomite_ABM import Agent

def run_model(m):
    m.run()
    return np.array(m.output)

class HouseholdModel(object):

    def __init__(self,child,householdsize,householdid,param):
        self.child = child
        self.initState = self.child.state
        self.agentDict = {}
        self.N = householdsize
        self.id = householdid
        ### Initialize rate parameters
        self.timestamp = dt.timedelta()
        self.beta = param['beta']        
        self.latentShape = param['latentShape']
        self.infectiousShape = param['infectiousShape']
        self.latentRate = 1/float(param['latentScale'])
        self.infectiousRate = 1/float(param['infectiousScale'])
        self.numDays = param['numDays']

        ### Initialize event dictionary
        self.eventDict = self.init_event_dict()

        self.init_agent_lists()

        self.output = None

        self.initialize_household()

        self.update_event_rates()
        #print self.susceptibleAgents

    def run(self):
        #tF = self.child.recoveryTime.total_seconds()/float(3600)
        tF = self.numDays
        t = 0
        while t < tF:
            if self.totalRate == 0:
                break
            else:
                dh = self.draw_event_time()
                event = self.draw_event()
                t += dh
                self.timestamp = dt.timedelta(days=t)
                self.advance_state(self.eventDict[event][0])
                self.update_event_rates()

        self.compile_output()

    def draw_event_time(self):
        return np.random.exponential(scale=1/float(self.totalRate))

    def draw_event(self):
        r = np.random.random()
        s = 0.0
        for event, rate in self.eventDict.iteritems():
            s += rate[1]/float(self.totalRate)
            if r < s:
                return event
        return event

    def advance_state(self,state):
        i = pr.choice(self.stateLists[state])
        a = self.agentDict[i]
        a.state += 1
        self.stateLists[state].remove(i)
        self.stateLists[state+1].append(i)
        a.timestamp = self.timestamp
        a.data.append((self.timestamp,a.state))


    def init_event_dict(self):
        eventDict = {'infection': [0,0]}
        for i in range(1,self.latentShape+1):
            eventDict['latent progression '+str(i)] = [i,0]
        for i in range(1,self.infectiousShape+1):
            eventDict['infectious progression '+str(i)] = [self.latentShape+i,0]
        return eventDict

    def init_agent_lists(self):
        self.stateLists = {}
        for i in range(0,2+self.latentShape+self.infectiousShape):
            self.stateLists[i] = []

    def initialize_household(self):
        self.child.id = '0h' + str(self.id)
        self.agentDict['0h'+str(self.id)] = self.child
        self.stateLists[self.child.state].append(self.child.id)
        for i in xrange(1,self.N):
            agentId = str(i) + 'h' + str(self.id)
            a = Agent(agentId)
            self.agentDict[agentId] = a
            self.stateLists[0].append(agentId)

    def update_event_rates(self):
        # Susceptibles and contaminated neighbors may interact
        numInfectious = sum([len(self.stateLists[i]) for i in range(1+self.latentShape,1+self.latentShape+self.infectiousShape)])
        self.eventDict['infection'][1] = self.beta*len(self.stateLists[0])*numInfectious

        # Latent agents progress
        for i in range(1,self.latentShape+1):
            self.eventDict['latent progression ' + str(i)][1] = self.latentRate*len(self.stateLists[i])

        # Infectious agents progress
        for i in range(1,self.infectiousShape+1):
            self.eventDict['infectious progression ' + str(i)][1] = self.infectiousRate*len(self.stateLists[self.latentShape+i])
        self.totalRate = sum([value[1] for value in self.eventDict.values()])

    def compile_events(self):
        out = {}
        for i in self.agentDict.keys():
            a = self.agentDict[i]
            for entry in a.data:
                outRow = np.zeros((2+self.latentShape+self.infectiousShape))
                
                time = entry[0].total_seconds()/float(3600*24)
                if time in out.keys():
                    out[time][entry[1]] += 1
                else:
                    if time != 0:
                        outRow[entry[1]-1] = -1
                        outRow[entry[1]] = 1
                        out[time] = outRow
  
        return np.array([[k,]+list(out[k]) for k in sorted(out)]) 
    
    def compile_output(self):
        eventList = self.compile_events()
        initRow = np.zeros((3+self.latentShape+self.infectiousShape))
        initRow[1] = self.N-1
        initRow[self.initState+1] = 1
        outArray = np.zeros((eventList.shape[0]+1,3+self.latentShape+self.infectiousShape))
        outArray[0,:] = initRow
        for i, row in enumerate(eventList):
            newRow = np.zeros((3+self.latentShape+self.infectiousShape))
            newRow[0] = row[0]
            newRow[1:] = outArray[i,1:] + row[1:]
            outArray[i+1] = newRow
        self.output = outArray
    
    def secondary_cases(self):
        if self.output is None:
            self.compile_output()
        return (self.N - 1) - self.output[-1,1]

if __name__ == '__main__':
    import json
    from sickchildcare_parser import *
    
    c = Agent('0h1',1,recoverytime=dt.timedelta(days=5))
    householdSize = 4
    jsonParams = open('noro_household_params.json').read()
    param = json.loads(jsonParams)
    param['numDays'] = 21
    '''
    m = HouseholdModel(c,householdSize,1,param)
    m.run()
    
    print m.secondary_cases()
    '''
    #pl.plot(out[:,0],out[:,1])
    #pl.show()
    #childList = cases_to_agents('data_export.tsv','all','e',1/float(3))

    childList = inc_to_agents('all_e.csv',1)
    householdSize = 4
    #param = {'beta': 0.075, 'latentShape':4,'latentRate':1,'infectiousShape':3,'infectiousRate':1, 'dayLength': 8, 'numDays': 7}

    outData = []
    id = 0
    for child in childList:
        initDay = child.timestamp.days
        m = HouseholdModel(child,householdSize,id,param)
        m.run()
        outData.append((initDay,m.secondary_cases()))
        #data = np.array(m.output)
        #outData.append(np.sum(data[:,3]))
        id += 1
    outData = np.array(outData)
    #print outData
    print np.sum(outData[:,1])
    print np.mean(outData[:,1])
