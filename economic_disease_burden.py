import numpy as np
import pandas as pd
import scipy.stats as ss
import random
from math import *
from household_model import *

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
        self.daylength = 0
        self.output = []
        global _bot, _top
        _bot = bot
        _top = top

    def run(self, days=0, daylength=0):
        self.days = days
        self.daylength = int(daylength)
        self.running = [0]
        self.daily = [0]
        self.gen_metadata(self.agents, self.devolvement_rate)
        for day in range(1,days):
            daycost = float(self.materials(self.mats) + self.labor(self.absrate, self.labor_hours, self.labor_wage) + self.opportunity_cost(self.agents, self.tuition_rate, self.clinic_cost, day, self.daylength))
            previous = self.running[-1]
            self.running.append(previous + daycost)
            self.daily.append(daycost)
        self.output = list(zip(self.running, self.daily))
        print(self.output)

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
            
            param = {'contactRateHH': 0.1, 'incubationRate': 1/float(24), 'recoveryRate': 1/float(3*24), 'dayLength': 16, 'numDays': self.days}
            #recoveryTime = dt.datetime(hours=np.random.exponential(scale=1/float(param['recoveryRate']))).total_seconds()/float(3600)
            #temp = Agent(1,2,recoverytime=recoveryTime)
            child = i
            m = HouseholdModel(child,householdSize,1,param)
            m.run()
            metadata['house'] = m.output
            kid_data[i] = metadata
        ses_list = range_sampler(_bot,_top,len(agents))
        for child in agents:
            v = kid_data.get(child)
            v['ses'] = random.choice(ses_list)
        print(kid_data)

    def opportunity_cost(self, agents, tuition_rate=0.0, clinic_cost=0.0, day=0, daylength=0):
        from fomite_ABM import timestamp_to_hours
        daycost = 0.0
        for child in agents:
            adj_data = []
            _curday = 0
            for i in range(1,len(child.data)):
                _daydelta = int(child.data[i][0].days)
                _oldstate = int(child.data[i-1][1])
                _newstate = int(child.data[i][1])
                for j in range(_daydelta):
                    adj_data.append([_curday,_oldstate])
                    _curday+=1
            for state in adj_data:
                if state[0] == day and state[1] == 3:
                    daycost += tuition_rate
                    temp = 0
                    if kid_data[child]['is_hos']:
                        print('child is hospitalized')
                        daycost += clinic_cost
                    temp = float(kid_data[child]['house'][day][2])/float(householdSize)
                    print(temp)
                    print(kid_data[child]['ses']/365.0)
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

def simple_costs(caseList, costParams, diseaseParams):
    providerProb = costParams['careProbability']
    primaryCareProb = costParams['primaryCare']['probability']
    primaryCareCost = costParams['primaryCare']['cost']
    urgentCareProb = costParams['urgentCare']['probability']
    urgentCareCost = costParams['urgentCare']['cost']
    ERProb = costParams['ER']['probability']
    ERCost = costParams['ER']['cost']
    meanIncome = costParams['income']['mean']
    incomeShape = costParams['income']['shape']
    incomeScale = costParams['income']['scale']

    adultPrimaryCareProb = diseaseParams['primaryCareProb']
    adultERProb = diseaseParams['ERProb']

    HHsizes = costParams['household']['size']
    HHdist = costParams['household']['proportion']

    outputData = {}
    id = 0
    for case in caseList:
        if case.timestamp.days < 356*4:
            outputData[id] = {}
            outputData[id]['day'] = case.timestamp.days
            sickDays = ceil(ss.gamma.rvs(diseaseParams['symptomaticShape'],loc=0,scale=diseaseParams['symptomaticScale']))
            #print sickDays
            #parentIncome = ss.expon.rvs(loc=0,scale=meanIncome)
            parentIncome = ss.gamma.rvs(incomeShape,0,incomeScale)
            parentIncomeLost = parentIncome*sickDays/float(260)
            HHsize = np.random.choice(a=HHsizes,size=1,p=HHdist)

            indirectCost = parentIncomeLost
            directCost = 0
            if random.random() < providerProb:
                if random.random() < primaryCareProb:
                    directCost += primaryCareCost
                if random.random() < urgentCareProb:
                    directCost += urgentCareCost
                if random.random() < ERProb:
                    directCost += ERCost

            m = HouseholdModel(case,HHsize,id,diseaseParams)
            m.run()
            secondaryCases = m.secondary_cases()
            for c in xrange(int(secondaryCases)):
                if random.random() < adultPrimaryCareProb:
                    directCost += primaryCareCost
                if random.random() < adultERProb:
                    directCost += ERCost
                sickDays = ceil(ss.gamma.rvs(diseaseParams['symptomaticShape'],loc=0,scale=diseaseParams['symptomaticScale']))
                incomeLost = parentIncome*sickDays/float(260)
                indirectCost += incomeLost

            totalCost = directCost + indirectCost
            outputData[id]['total cost'] = totalCost
            outputData[id]['indirect cost'] = indirectCost
            outputData[id]['direct cost'] = directCost
            outputData[id]['secondary cases'] = secondaryCases
            id += 1

    return outputData

def cost_stats(costData):
    costList = [costData[i]['total cost'] for i in costData]
    directCostList = [costData[i]['direct cost'] for i in costData]
    indirectCostList = np.array(costList) - np.array(directCostList)
    avgCases = len(costList)/float(4)
    avgCaseCost = np.mean(costList)
    avgDirectCost = np.mean(directCostList)
    avgIndirectCost = np.mean(indirectCostList)
    annualCost = np.sum(costList)/float(4)
    secondaryCases = np.mean([costData[i]['secondary cases'] for i in costData])
    print 'average yearly cases : ', avgCases
    print 'average cost per case : ', avgCaseCost
    print 'average direct costs : ', avgDirectCost
    print 'average indirect costs : ', avgIndirectCost
    print 'average annual cost : ', annualCost 
    print 'average secondary cases : ', secondaryCases

if __name__ == '__main__':
    import json
    import matplotlib.pyplot as pl
    from sickchildcare_parser import *
    jsonEconParams = open('cost_params.json').read()
    costParams = json.loads(jsonEconParams)
    agentList = inc_to_agents('all_e.csv',1/float(3))

    jsonDiseaseParams = open('noro_household_params.json').read()
    diseaseParams = json.loads(jsonDiseaseParams)
    diseaseParams['numDays'] = 21
    costs = simple_costs(agentList,costParams,diseaseParams)

    cost_stats(costs)
    #print costs['day']
    #cumCosts = costs['cost'].cumsum()
    #cumCases = costs['cases'].cumsum()
    #pl.tight_layout()
    '''
    pl.scatter(costs['day'],costs['cost'])
    pl.xlabel('Day')
    pl.ylabel('Total cost')
    pl.tight_layout()
    pl.figure()
    pl.plot(costs['day'],cumCosts)
    pl.xlabel('Day')
    pl.ylabel('Cumulative cost')
    pl.tight_layout()
    avgCases = np.sum(costs['cases'])/float(4)
    avgCost = np.sum(costs['cost'])/float(4)
    print 'avg annual cases', avgCases
    print 'avg annual cost', avgCost
    print 'avg cost/case', avgCost/float(avgCases)
    pl.show()
    #test()
    '''
    