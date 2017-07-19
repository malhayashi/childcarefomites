import numpy as np
import networkx as nx
import random as pr
import matplotlib.pyplot as pl
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
        self.tF = param['numDays']
        self.t = 0
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
        for t in xrange(self.tF):
            self.output.append([len(self.susceptibleAgents),len(self.incubatingAgents),len(self.infectedAgents), self.t])
            h = 0
            for i in self.agentDict:
                a = self.agentDict[i]
                a.timestamp = h
                if a.contamination == 0 and a.state == 1:
                    a.state = 0
                    self.update_contact_pairs(i)

            while h < self.dayLength:

                if self.totalRate > 0:
                    dh = self.draw_event_time()
                    if dh < self.dayLength - h:
                        event = self.draw_event()
                        print event
                        self.resolve(event)
                        self.update_event_rates()
                        h += dh
                        self.t += dh
                    else:
                        break
                else:
                    break
            self.t = t

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

        self.agentDict[j].state == 2
        self.susceptibleAgents.remove(j)
        self.incubatingAgents.append(j)

        self.child.timestamp = self.t
        self.agentDict[j].timestamp = self.t

    def present(self):
        i = pr.choice(self.incubatingAgents)
        #print ' ', i, 'developed symptoms'
        a = self.agentDict[i]
        a.state == 3
        self.incubatingAgents.remove(i)
        self.infectedAgents.append(i)

    def recover(self):
        i = pr.choice(self.infectedAgents)
        #print ' ', i, 'recovered'
        self.agentDict[i].state = 4
        self.infectedAgents.remove(i)

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

if __name__ == '__main__':
    c = Agent(1,2)
    householdSize = 4
    param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': 7}
    m = HouseholdModel(c,householdSize,1,param)
    m.run()

    print m.output