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
        self.betaHH = param['contactRateHH']        
        self.latentShape = param['latentShape']
        self.infectiousShape = param['infectiousShape']
        self.incubationRate = param['incubationRate']
        self.recoveryRate = param['recoveryRate']
        self.dayLength = param['dayLength']

        ### Initialize event dictionary
        self.events = self.init_events()

        self.susceptibleAgents = []
        self.incubatingAgents = []
        self.infectedAgents = []
        self.output = []

        self.initialize_household()

        self.init_event_rates()
        
        self.events['human contact'] = self.betaHH*len(self.susceptibleAgents)
        # Infectious agents can recover
        self.events['recovery'] = len(self.infectedAgents)*self.recoveryRate
        # Incubating agents develop symptoms
        self.events['symptom presentation'] = self.incubationRate*len(self.incubatingAgents)
        self.totalRate = np.sum(self.events.values())
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
                self.resolve(event)
                self.update_event_rates()
                t += dh
                self.timestamp = dt.timedelta(hours=t)

        self.compile_output()

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
        #print self.susceptibleAgents
        j = pr.choice(self.susceptibleAgents)
        a = self.agentDict[j]
        a.state = 2
        self.susceptibleAgents.remove(j)
        self.incubatingAgents.append(j)
        self.child.timestamp = self.timestamp
        a.timestamp = self.timestamp
        a.data.append((self.timestamp,a.state))

    def present(self):
        i = pr.choice(self.incubatingAgents)
        #print ' ', i, 'developed symptoms'
        a = self.agentDict[i]
        a.state = 3
        self.incubatingAgents.remove(i)
        self.infectedAgents.append(i)
        a.timestamp = self.timestamp
        a.data.append((self.timestamp,a.state))

    def recover(self):
        i = pr.choice(self.infectedAgents)
        #print ' ', i, 'recovered'
        a = self.agentDict[i]
        a.state = 4
        self.infectedAgents.remove(i)
        a.timestamp = self.timestamp
        a.data.append((self.timestamp,a.state))

    def init_event_rates(self):
        eventDict = {'infection': 0,
                     'infectiousness': 0,
                     'recovery': 0}
        for i in range(1,self.latentShape):
            eventDict['latent'+str(i)] = 0
        for i in range(1,self.infectiousShape):
            eventDict['infectious'+str(i)] = 0

        return eventDict

    def make_latent_event(self,latentNum):
        name = 'latent' + str(latentNum)
        def latent():
            oldState = 1+latentNum
            i = pr.choice(getattr(self,'state'+str(oldState)+'List')
            a = self.agentDict[i]
            a.state += 1
            self.update_state_lists(oldState,a.state)
            a.timestamp = self.timestamp
            a.data.append((self.timestamp,a.state))

        setattr(self,name,latent)
        
    def make_infectious_event(self,infectiousNum):
        name = 'infectious' + str(infectiousNum)
        def infectious():
            oldState = 1 + self.latentShape + infectiousNum
            i = pr.choice(getattr(self,'state'+str(oldState)+'List')
            a = self.agentDict[i]
            a.state += 1
            self.update_state_lists(oldState,a.state)
            a.timestamp = self.timestamp
            a.data.append((self.timestamp,a.state))

        setattr(self,name,infectious)

    def init_dispatch(self):
        fcnDict = {'infection': self.infect,
                   'infectiousness': self.present,
                   'recovery': self.recover,
        }
        for i in range(1,self.latentShape):
            name = 'latent'+str(i)
            fcnDict[name] = getattr(self,name)

        for i in range(1,self.infectiousShape):
            name = 'infectious'+str(i)
            fcnDict[name] = getattr(self,name)

        return fcnDict

    def initialize_household(self):
        for i in xrange(self.N-1):
            agentId = str(i) + 'h' + str(self.id)
            a = Agent(agentId)
            self.agentDict[agentId] = a
            self.susceptibleAgents.append(agentId)

    def update_event_rates(self):
        # Susceptibles and contaminated neighbors may interact
        self.events['human contact'] = self.betaHH*len(self.susceptibleAgents)
        # Infectious agents can recover
        self.events['recovery'] = len(self.infectedAgents)*self.recoveryRate
        # Incubating agents develop symptoms
        self.events['symptom presentation'] = self.incubationRate*len(self.incubatingAgents)
        self.totalRate = np.sum(self.events.values())

    def resolve(self,event):
        dispatch = {
            'human contact': self.contact,
            'recovery': self.recover,
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