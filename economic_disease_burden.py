import numpy as np
import random
from math import *

class Forecast(object):

    def __init__(self):
        pass

    def __init__(self, agent_list=(), materials=None, absrate=None, labor_hours=0.0, labor_wage=0.0, tuition_rate=0.0, devolvement_rate=0.0, clinic_cost=0.0, bot=0.0, top=0.0):
        self.agents = agent_list
        self.mats = materials
        self.absrate = absrate
        self.labor_hours = labor_hours
        self.labor_wage = labor_wage
        self.tuition_rate = tuition_rate
        self.devolvement_rate = devolvement_rate
        self.clinic_cost = clinic_cost
        self.days = 0
        self.output = []
        global _bot, _top
        _bot = bot
        _top = top

    def run(self, days=0):
        self.days = days
        self.running = [0]
        self.gen_metadata(self.agents, self.devolvement_rate)
        for day in range(1,days):
            daycost = float(self.materials(self.mats) + self.labor(self.absrate, self.labor_hours, self.labor_wage) + self.opportunity_cost(self.agents, self.tuition_rate, self.clinic_cost, day))
            previous = self.running[-1]
            self.running.append(previous + daycost)
        print(self.running)

    def materials(self, mats=None, materials_touse=None):
        total = 0.0
        if mats is not None and isinstance(mats, dict):
            for k,v in mats.iteritems():
                itemcost = v[0]*v[1]
                total += itemcost
        return total

    def labor(self, absrate=None, hours=0.0, wage=0.0):
        if absrate is not None:
            return float(hours*wage)
        else:
            return float(absrate)

    def gen_metadata(self, agents, devolvement_rate=0.0):
        global kid_data, householdSize
        kid_data = {}
        from fomite_ABM import Agent, Model
        from household_model import HouseholdModel
        from Numericals import range_sampler
        for i in agents:
            metadata = {'ses':0.0, 'is_hos':False, 'house':[]}
            choice = np.random.uniform(0,1.0)
            if choice < devolvement_rate:
                metadata['is_hos'] = True
            householdSize = 4
            temp = Agent(1,2)
            param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': self.days}
            m = HouseholdModel(temp,householdSize,1,param)
            m.run()
            metadata['house'] = m.output
            kid_data[i] = metadata
        ses_list = range_sampler(_bot,_top,len(agents))
        print(kid_data)
        for child in agents:
            v = kid_data.get(child)
            v['ses'] = random.choice(ses_list)
        print(kid_data)

    def opportunity_cost(self, agents, tuition_rate=0.0, clinic_cost=0.0, day=0):
        daycost = 0.0
        for child in agents:
            for index in child.data:
                t = int(index[0]/(8))
                print(t)
                if t == day and index[1] == 3:
                    daycost += tuition_rate
                    temp = 0
                    if kid_data[child]['is_hos']:
                        print('child is hospitalized')
                        daycost += clinic_cost
                    print(kid_data[child]['house'].pop(0))
                    daycost += temp*kid_data[child]['ses']/365.0
        return daycost

def socioeconomic_clustering(X):
    val = 1.0/sqrt(2*variance*pi)*exp(-(X-mu)**2/(2*variance))
    print(val)
    return val

def test():
    mat = {'clorox':10.0, 'H2O2':20.50}
    touse = {'clorox':.1, 'H2O2':.5}
    a = Forecast()
    print(a.materials(mat, touse))


if __name__ == '__main__':
    test()
