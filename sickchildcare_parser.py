#!/usr/bin/python
import sys
import datetime as dt 
import pandas as pd

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
#print centerList

disease = raw_input('(E)nteric or (R)espiratory: ').lower()
center = raw_input('Center name: ').translate(None,'-\' ').lower()

with open('data_export.tsv') as f:

    ### Process header
    header = f.readline().strip().split('\t')
    colDict = {}
    for i, colName in enumerate(header):
        colDict[colName] = i
    #print colDict

    if disease == 'e':
        cols = (11,)
    else:
        cols = (9,12,13)

    out = ['line,date,cases']
    dateDict = {}
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
                if date in dateDict:
                    dateDict[date] += 1
                else:
                    dateDict[date] = 1

if len(dateDict.items()) > 0:
    data = pd.DataFrame(sorted(dateDict.items()),columns=['date','cases'])
    
    data.to_csv(center+'_'+disease+'.csv')
    #print data
else:
    print 'no cases for this center'


        

    