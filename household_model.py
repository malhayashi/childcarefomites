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
        self.agentDict = {}
        self.N = householdsize
        self.id = householdid
        ### Initialize rate parameters
        self.timestamp = dt.timedelta()
        self.beta = param['beta']        
        self.latentShape = param['latentShape']
        self.infectiousShape = param['infectiousShape']
        self.latentRate = param['latentRate']
        self.gamma = param['gamma']
        self.dayLength = param['dayLength']

        ### Initialize event dictionary
        self.eventDict = self.init_event_dict()

        self.init_agent_lists()

        self.output = []

        self.initialize_household()

        self.update_event_rates()
        #print self.susceptibleAgents

    def run(self):
        tF = self.child.recoveryTime.total_seconds()/float(3600)
        t = 0
        while t < tF:
            if self.totalRate == 0:
                break
            else:
                dh = self.draw_event_time()
                event = self.draw_event()
                #print event
                self.advance(self.eventDict[event][0])
                self.update_event_rates()
                t += dh
                self.timestamp = dt.timedelta(hours=t)

        self.compile_output()

    def draw_event_time(self):
        return np.random.exponential(scale=1/float(self.totalRate))

    def draw_event(self):
        r = np.random.random()
        s = 0.0
        for event, rate in self.eventDict.iteritems():
            s += rate/float(self.totalRate)
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
        eventDict = {'infection': [1,0]}
        for i in range(1,self.latentShape):
            eventDict['latent progression '+str(i)] = [1+i,0]
        for i in range(1,self.infectiousShape):
            eventDict['infectious progression '+str(i)] = [1+self.latentShape+i,0]
        return eventDict

    def init_agent_lists(self):
        for i in range(1,3+latentNum+infectiousNum):
            self.stateLists[i] = []

    def initialize_household(self):
        for i in xrange(self.N-1):
            agentId = str(i) + 'h' + str(self.id)
            a = Agent(agentId)
            self.agentDict[agentId] = a
            self.susceptibleAgents.append(agentId)

    def update_event_rates(self):
        # Susceptibles and contaminated neighbors may interact
        self.events['infection'][1] = self.beta*len(self.stateLists[1])

        # Latent agents progress
        for i in range(1,latentShape+1):
            self.events['latent progression ' + str(i)][1] = self.latentRate*len(self.stateLists[1+i])

        # Infectious agents progress
        for i in range(1,infectiousShape+1):
            self.events['infectious progression ' + str(i)][1] = self.gamma*len(self.stateLists[1+self.latentShape+i])
        self.totalRate = np.sum(self.events.values())

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
    from sickchildcare_parser import *
    '''
    c = Agent(1,2,recoverytime=dt.timedelta(days=5))
    householdSize = 4
    param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': 7}
    m = HouseholdModel(c,householdSize,1,param)
    m.run()
    
    print m.output
    '''
    childList = cases_to_agents('data_export.tsv','all','e',1/float(3))
    householdSize = 4
    param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': 7}

    outData = []
    id = 0
    for child in childList:
        m = HouseholdModel(child,householdSize,id,param)
        m.run()
        data = np.array(m.output)
        outData.append(np.sum(data[:,3]))
        id += 1
    print np.mean(outData)
    print np.std(outData)