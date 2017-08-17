#!/usr/bin/python
import sys, os
import datetime as dt 
import pandas as pd

#print centerList

#disease = raw_input('(E)nteric or (R)espiratory: ').lower()
#center = raw_input('Center name: ').translate(None,'-\' ').lower()

def write_inc_csv(fName, centerName, caseType):
    data = parse_cases(fName, centerName, caseType)

    if len(dateDict.items()) > 0:
        data = pd.DataFrame(sorted(dateDict.items()),columns=['date','cases'])
        
        data.to_csv(center+'_'+disease+'.csv')
        #print data
    else:
        print 'no cases for this center'

def cases_to_agents(fName, centerName, caseType, recoveryRate):
    from fomite_ABM import Agent
    from numpy.random import exponential

    data = parse_cases(fName, centerName, caseType)
    firstDate = sorted(data.keys())[0]
    agentList = []
    dummyId = 0
    for date in sorted(data):
        numCases = data[date]
        relDate = (date-firstDate).days
        
        while numCases > 0:
            newCase = Agent(id=dummyId,state=3,recoverytime=exponential(1/float(recoveryRate)))
            newCase.day = relDate
            agentList.append(newCase)
            dummyId += 1
            numCases -= 1
    return agentList

def parse_cases(fName, centerName, caseType):
    ## note: move center list to a file
    centerList = ['Adventure Center Childcare',
    'Annie\'s Children\'s Center Downtown',
    'Bemis Farm',
    'Bemis Farms 2 (Lincoln)',
    'Childtime Learning Center - Plymouth Road',
    'Community Day Care Inc.',
    'Dorothy\'s Discovery Daycare Center',
    'Gretchen\'s House - Mt. Pleasant',
    'Foundations Preschool of Washtenaw County',
    'Lil\' Saints Preschool',
    'Morning Star Child Care',
    'WCC Children\'s Center',
    'Head Start - Ford',
    'Head Start - Perry Early Learning Center',
    'Head Start - Whitmore Lake',
    'Head Start - Ann Arbor',
    'Head Start - Beatty Early Learning Center',
    'The Discovery Center Preschool',
    'UM - Glazier',
    'Gretchen\'s House Dhu Varren',
    'Gretchen\'s House Oak Valley',
    'UM - Towsley Children\'s House',
    'UM - North Campus Children\'s Center',
    'Apple Play: Green Apple Garden',
    'Apple Play Manzanitas',
    'Play and Learn Children\'s Place',
    'Jelly Bean Daycare and Preschool']

    centerList = [c.translate(None,'-\' ').lower() for c in centerList]
    center = centerName.translate(None,'-\' ').lower()
    disease = caseType.lower()[0]
    with open(fName) as f:
        ### Process header
        header = f.readline().strip().split('\t')
        colDict = {}
        for i, colName in enumerate(header):
            colDict[colName] = i

        if disease == 'e':
            cols = (11,)
        else:
            cols = (9,12,13)

        out = ['line,date,cases']
        dataDict = {}
        for i, line in enumerate(f.readlines()):
            line = line.strip().split('\t')
            if center == 'all':
                testCenter = 'all'
            else:
                testCenter = line[1].translate(None,'-\' ').lower()
            #print testCenter
            #print [line[col] for col in cols]
            testDisease = sum([int(line[col]) for col in cols])
            if testDisease > 0:
                if center == testCenter:
                    #date = dt.datetime.strptime(line[0],'%m/%d/%Y').date()
                    date = dt.datetime.strptime(line[0],'%m/%d/%Y')
                    if date in dataDict:
                        dataDict[date] += 1
                    else:
                        dataDict[date] = 1

    return dataDict

if __name__ == '__main__':
    ### Test code -- change directory as needed
    cases_to_agents(os.path.join('C:/','Users','Michael','Dropbox','Projects','Fomites','Data','data_export.tsv'),'all','e',5)
        

