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
        self.incubationRate = param['incubationRate']
        self.recoveryRate = param['recoveryRate']
        self.dayLength = param['dayLength']

        ### Initialize event dictionary
        self.events = {
            'human contact': 0,
            'recovery': 0,
            'symptom presentation': 0
        }

        self.susceptibleAgents = []
        self.incubatingAgents = []
        self.infectedAgents = []
        self.output = []

        self.initialize_household()

        self.events['human contact'] = self.betaHH*len(self.susceptibleAgents)
        # Infectious agents can recover
        self.events['recovery'] = len(self.infectedAgents)*self.recoveryRate
        # Incubating agents develop symptoms
        self.events['symptom presentation'] = self.incubationRate*len(self.incubatingAgents)
        self.totalRate = np.sum(self.events.values())
        print self.susceptibleAgents

    def run(self):
        tF = self.child.recoveryTime.total_seconds()/float(3600)
        t = 0
        while t < tF:
            if self.totalRate == 0:
                break
            else:
                dh = self.draw_event_time()
                event = self.draw_event()
                print event
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
    c = Agent(1,2,recoverytime=dt.timedelta(days=5))
    householdSize = 4
    param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': 7}
    m = HouseholdModel(c,householdSize,1,param)
    m.run()

    print m.output