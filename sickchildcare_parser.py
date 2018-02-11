#!/usr/bin/python
import sys, os
import numpy as np
import datetime as dt 
import pandas as pd

#print centerList

#disease = raw_input('(E)nteric or (R)espiratory: ').lower()
#center = raw_input('Center name: ').translate(None,'-\' ').lower()

def write_inc_csv(fName, centerName, caseType):
    dataDict = parse_cases(fName, centerName, caseType)

    if len(dataDict.items()) > 0:
        data = pd.DataFrame(sorted(dataDict.items()),columns=['date','cases'])
        
        data.to_csv(centerName+'_'+caseType+'.csv')
        #print data
    else:
        print 'no cases for this center'

def inc_to_agents(fName, recoveryRate):
    from fomite_ABM import Agent
    from numpy.random import exponential
    data = pd.read_csv(fName,delimiter=',',index_col=0)
   
    data['date'] = pd.to_datetime(data['date'])
    data['date'] = data['date'] - data['date'][0] 

    agentList = []
    dummyId = 0
    for row in data.iterrows():
        numCases = row[1]['cases']
        relDate = row[1]['date']
        for i in range(numCases):
            recover = dt.timedelta(days=exponential(1/float(recoveryRate)))
            newCase = Agent(id=dummyId,state=2,recoverytime=recover)
            newCase.timestamp = relDate
            newCase.data.append((relDate,2))
            agentList.append(newCase)
            dummyId += 1

    return agentList

def cases_to_agents(fName, centerName, caseType, recoveryRate):
    from fomite_ABM import Agent
    from numpy.random import exponential

    data = parse_cases(fName, centerName, caseType)
    firstDate = sorted(data.keys())[0]
    agentList = []
    dummyId = 0
    for date in sorted(data):
        numCases = data[date]
        #relDate = (date-firstDate).days
        relDate = date - firstDate
        #print relDate
        while numCases > 0:
            recover = dt.timedelta(days=exponential(1/float(recoveryRate)))
            newCase = Agent(id=dummyId,state=3,recoverytime=recover)
            #print newCase.recoveryTime
            newCase.timestamp = relDate
            newCase.data.append((relDate,3))
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
            #print line
            try:
                testDisease = sum([int(line[col]) for col in cols])
            except (IndexError, ValueError):
                print i, line
            if testDisease > 0:
                if center == testCenter:
                    #date = dt.datetime.strptime(line[0],'%m/%d/%Y').date()
                    date = dt.datetime.strptime(line[0],'%m/%d/%Y')
                    if date in dataDict:
                        dataDict[date] += 1
                    else:
                        dataDict[date] = 1

    return dataDict

def clean(fName):
    with open(fName) as fIn, open(os.path.join(os.path.dirname(fName),'clean.tsv'),'w') as fOut:
        
        outLines = []
        fList = list(fIn)
        head = fList[0].strip()
        headLen = head.count('\t')

        #fOut.write(head+'\n')
        prevLine = head
        for i, line in enumerate(fList[1:]):
            line = line.strip()
            propLine = prevLine + line
            propLen = propLine.count('\t')
            if propLen in (headLen, headLen-1):
                print i, propLine
                prevLine = propLine
            else:
                fOut.write(prevLine+'\n')
                prevLine = line
            #if lineLen < (headLen-1):
            #    print i, lineLen
                    



if __name__ == '__main__':
    ### Test code -- change directory as needed
    #cases_to_agents(os.path.join('D:/','micha','Dropbox','Projects','Fomites','Data','data_export.tsv'),'all','e',1/float(5))
    #write_inc_csv(os.path.join('C:/','Users','micha','Dropbox','Projects','Fomites','Data','data_export.tsv'),'all','e')    
    #inc_to_agents('all_e.csv',1/float(5))
    #clean(os.path.join('D:/','micha','Dropbox','Projects','Fomites','Data','data_export_curr.tsv'))
    write_inc_csv(os.path.join('D:/','micha','Dropbox','Projects','Fomites','Data','clean.tsv'),'all','e')
    #clean(os.path.join(os.path.expanduser('~'),'Dropbox','Projects','Fomites','Data','data_export_curr.tsv'))

