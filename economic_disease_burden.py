import numpy as np
import random
from math import *

class Forecast(object):

    def __init__(self):
        pass

    def __init__(self, agent_list=(), materials=None, materials_touse=None, absrate=None, labor_hours=0.0, labor_wage=0.0, tuition_rate=0.0, devolvement_rate=0.0, clinic_cost=0.0):
        self.agents = agent_list
        self.mats = materials
        self.materials_touse = materials_touse
        self.absrate = absrate
        self.labor_hours = labor_hours
        self.labor_wage = labor_wage
        self.tuition_rate = tuition_rate
        self.clinic_cost = clinic_cost
        self.days = 0
        self.output = []

    def run(self, days=0):
        self.days = days
        self.running = [0]
        self.gen_metadata(self.agents, self.devolvement_rate)
        for day in range(0,days):
            daycost = float(self.materials(self.mats, self.materials_touse) + self.labor(self.absrate, self.labor_hours, self.labor_wage) + self.opportunity_cost(self.tuition_rate, self.clinic_cost, day))
            previous = running[-1]
            self.running.append(previous + daycost)

    def materials(self, mats=None, materials_touse=None):
        total = 0.0
        if mats is not None and isinstance(mats, dict):
            if materials_touse is not None and isinstance(materials_touse, dict):
                for unit in materials_touse:
                    itemcost = mats[unit]*materials_touse[unit]
                    total += itemcost
        return total

    def labor(self, absrate=None, hours=0.0, wage=0.0):
        if absrate is not None:
            return float(hours*wage)
        else:
            return float(absrate)

    def gen_metadata(self, agents, devolvement_rate=0.0):
        global kid_data, householdSize
        from fomite_ABM import Agent, Model
        from household_model import HouseholdModel
        from Numericals import Numericals
        for i in agents:
            sickdays = 0
            metadata = {'sick_days': 0, 'ses':0.0, 'is_hos':False, 'house':[]}
            for j in i.data:
                if j[1] == 1:
                    sickdays+=1
            metadata['sick_days'] = sickdays
            choice = np.random.uniform(0,1.0)
            if devolvement_rate < choice:
                metadata['is_hos'] = True
            householdSize = 4
            temp = Agent(1,2)
            param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': days}
            m = HouseholdModel(temp,householdSize,1,param)
            metadata['house'] = m.output
            kid_data[i] = metadata
        ses_list = metropolisHastings(distribution=lambda X: socioeconomic_clustering(X, 100000, 100), iterations=len(agents))
        for k,v in kid_data:
            v['ses'] = random.choice(ses_list)

    def opportunity_cost(self, tuition_rate=0.0, clinic_cost=0.0, day=0):
        daycost = 0.0
        for k,v in kid_data:
            for index in k.data:
                if index[0] == day and index[1] == 3:
                    daycost += tuition_rate
                    v['sick_days'] -= 1
                    if v['is_hos']:
                        daycost += clinic_cost
                    daycost += float(v['house'].pop(0)[2]/householdSize*v['ses'])
        return daycost

    def socioeconomic_clustering(X, mean, variance):
        return 1.0/sqrt(2*variance*pi)*exp(-(X-mean)**2/(2*variance))

def test():
    mat = {'clorox':10.0, 'H2O2':20.50}
    touse = {'clorox':.1, 'H2O2':.5}
    a = Forecast()
    print(a.materials(mat, touse))


if __name__ == '__main__':
    test()
