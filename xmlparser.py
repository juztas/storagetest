# sphinx_gallery_thumbnail_number = 3
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.cbook as cbook
import numpy as np
import os
import copy
import sqlite3
import datetime
import json
import pandas as pd
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join


MAINDIR='NANO_PERF'
GOODJOBDIR='LOCAL'
#ALLDIRS = ['CEPH', 'CEPHCLIENT', 'HADOOP', 'HADOOP1', 'HADOOP2', 'LOCAL', 'REDIRFNAL', 'REDIRCaltech', 'CERN', 'REDIRCACHE', 'REDIRCACHE1', 'CACHEDIRECT', 'CACHEDIRECT1', 'CACHECERN', 'CACHECERN1', 'CACHECERN2', 'CACHECERN3', 'NDN', 'NDN1']
ALLDIRS = ['LOCAL', 'NDNVIP-80', 'NDN', 'NDN1', 'CACHECERN1', 'CACHECERN2', 'CACHECERN3']
#ALLDIRS = ['smartiops', 'samsung-ssd-850', 'hp-ssd-ex920-512gb', 'LOCAL', 'CACHECERN']


PERFKEYS= ['AvgEventTime', 'EventSetup Get', 'EventSetup Lock', 'EventThroughput', 'MaxEventTime', 'MinEventTime', 'NumberOfStreams', 'NumberOfThreads', 'TotalInitCPU', 'TotalInitTime', 'TotalJobCPU', 'TotalJobTime', 'TotalLoopCPU', 'TotalLoopTime']

TIMINGKEYS=[]

def scandir(DIRNAME):
    path = '%s/%s/' % (MAINDIR, DIRNAME)
    try:
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    except OSError:
        # Means dir does not exist yet
        return {}, {}, {} 
    out = {}
    out.setdefault('Total-Time', [])
    outjobs = {}
    outperf = {}
    uniq = []
    for filename in onlyfiles:
        fileids = filename.split('-')
        totalMsecs = 0
        outjobs.setdefault(str(fileids[1]), {})
        outjobs[str(fileids[1])]['exitcode'] = fileids[2]
        outperf.setdefault(str(fileids[1]), {})
        outperf[str(fileids[1])]['exitcode'] = fileids[2]
        e = ET.parse("%s/%s" % (path, filename))
        out.setdefault('exitcodes', [])
        out['exitcodes'].append(fileids[2])
        for elt in e.iter():
            if 'Name' in elt.keys() and elt.get('Name').startswith('Timing'):
                out.setdefault(elt.get('Name'), [])
                out[elt.get('Name')].append(float(elt.get('Value')))
                outjobs[str(fileids[1])][elt.get('Name')] = float(elt.get('Value'))
            if 'Name' in elt.keys() and elt.get('Name')  in PERFKEYS:
                outperf[str(fileids[1])][elt.get('Name')] = float(elt.get('Value'))
    return out, outjobs, outperf

# Python program to get average of a list 
def average(lst):
    try: 
        return sum(lst) / len(lst)
    except ZeroDivisionError:
        return 0

def minimum(lst):
    try:
        return min(lst)
    except ValueError:
        return 0

def maximum(lst):
    try:
        return max(lst)
    except ValueError:
        return 0

def sumall(lst):
    return sum(lst)

def printsummary(keylist, indict, goodjobs):
    for key in keylist:
        linec = "JOBID;"
        line1 = ""
        i = 0
        for DIR in ALLDIRS:
            linec +="ExitCode;%s;" % key
            if i == 0:
                line1 +="%s; ;" % DIR
                i+=1
            else:
                line1 +="%s; ;" % DIR
        print line1
        print linec
        for jobid in range(1,401):
            lineout = ""
            if jobid not in goodjobs:
                continue
            lineout += "%s;" % jobid
            for DIR in ALLDIRS:
                if str(jobid) not in indict[DIR].keys():
                    lineout += "1000;"
                else:
                    lineout += '%s;' % indict[DIR][str(jobid)]['exitcode']
                if str(jobid) not in indict[DIR].keys():
                    lineout += "0;"
                elif key not in indict[DIR][str(jobid)].keys():
                    lineout += "0;"
                else:
                    lineout += "%s;" % indict[DIR][str(jobid)][key]
            print lineout

def getSummaryPerf(keylist, indict, goodjobs):
    linec = ""
    for key in keylist:
        linec += "%s;" % key
    #for key in keylist:
    #    linec += "%s;" % key
    print 'Type;%s;count' % linec
    for DIR in ALLDIRS:
        sums = {'success': {}, 'failures': {}}
        for jobid in range(1,401):
            if str(jobid) in indict[DIR].keys():
                for key in keylist:
                    if int(indict[DIR][str(jobid)]['exitcode']) == 0:
                        sums['success'].setdefault(key, [])
                        sums['success'][key].append(indict[DIR][str(jobid)][key])
                    else:
                        if key in indict[DIR][str(jobid)].keys():
                            sums['failures'].setdefault(key, [])
                            sums['failures'][key].append(indict[DIR][str(jobid)][key])
                        else:
                            sums['failures'].setdefault(key, [])
                            sums['failures'][key].append(0)
        nline = "%s;" % DIR
        bigcount = {'success': 0, 'failures': 0}
        #for subkey in ['success', 'failures']:
        for subkey in ['failures']:
            for key in keylist:
                if key in sums[subkey].keys():
                    tmpcount = len(sums[subkey][key])
                    bigcount[subkey] = tmpcount if tmpcount > bigcount[subkey] else bigcount[subkey]
                    nline += "%s;" % float(float(sum(sums[subkey][key]))/float(len(sums[subkey][key])))
                else:
                    bigcount[subkey] = 0
                    nline += "0;"
            print "%s;%s" % (nline, bigcount[subkey])

def getSummaryPerf1(keylist, indict, goodjobs):
    linec = ""
    for key in keylist:
        linec += "%s;" % key
    #for key in keylist:
    #    linec += "%s;" % key
    print 'Type;%s;count' % linec
    for DIR in ALLDIRS:
        sums = {'success': {}, 'failures': {}}
        for jobid in range(0,401):
                exitcode = 1000
                if len(indict[DIR]['exitcodes']) > jobid:
                    exitcode = int(indict[DIR]['exitcodes'][jobid])
                for key in keylist:
                    val = 0
                    if  key in indict[DIR].keys():
                        if len(indict[DIR][key]) > jobid:
                            val = indict[DIR][key][jobid]
                    if exitcode == 0:
                        if key in indict[DIR].keys():
                            sums['success'].setdefault(key, [])
                            sums['success'][key].append(val)
                        else:
                            sums['success'].setdefault(key, [])
                            sums['success'][key].append(0)
                    else:
                        if key in indict[DIR].keys():
                            sums['failures'].setdefault(key, [])
                            sums['failures'][key].append(val)
                        else:
                            sums['failures'].setdefault(key, [])
                            sums['failures'][key].append(0)
        nline = "%s;" % DIR
        bigcount = {'success': 0, 'failures': 0}
        #for subkey in ['success', 'failures']:
        for subkey in ['failures']:
            for key in keylist:
                if key in sums[subkey].keys():
                    tmpcount = len(sums[subkey][key])
                    bigcount[subkey] = tmpcount if tmpcount > bigcount[subkey] else bigcount[subkey]
                    nline += "%s;" % float(float(sum(sums[subkey][key]))/float(len(sums[subkey][key])))
                else:
                    bigcount[subkey] = 0
                    nline += "0;"
            print "%s;%s" % (nline, bigcount[subkey])

def Average(lst): 
    return sum(lst) / len(lst) 

def getAVGs(keylist, indict, goodjobs, onlyFailures=False):
    OUTs = {}
    for key in keylist:
        OUTs.setdefault(key, {})
        for jobid in range(1,401):
            if jobid not in goodjobs:
                continue
            for DIR in ALLDIRS:
                exitCode = 1000
                try:
                    exitCode = int(indict[DIR][str(jobid)]['exitcode'])
                except KeyError:
                    exitCode = 1000
                if onlyFailures:
                    if exitCode == 0:
                        continue
                OUTs[key].setdefault(DIR, [])
                if str(jobid) not in indict[DIR].keys():
                    OUTs[key][DIR].append(0)
                elif key not in indict[DIR][str(jobid)].keys():
                    OUTs[key][DIR].append(0)
                else:
                    OUTs[key][DIR].append(float(indict[DIR][str(jobid)][key]))
    for key in keylist:
        linec = ""
        line1 = ""
        i = 0
        for DIR in ALLDIRS:
            if i == 0:
                linec +=";%s;" % key
                line1 +=";%s;" % DIR
                i+=1
            else:
                linec +="%s;" % key
                line1 +="%s;" % DIR
        print line1
        print linec
        for typen in ['avg', 'min', 'max', 'sum']:
            lineout = "%s;" % typen
            for DIR in ALLDIRS:
                if DIR not in OUTs[key].keys():
                    lineout += "0;" 
                    continue
                elif typen == 'avg':
                    lineout += "%s;" % Average(OUTs[key][DIR])
                elif typen == 'min':
                    lineout += "%s;" % min(OUTs[key][DIR])
                elif typen == 'max':
                    lineout += "%s;" % max(OUTs[key][DIR])
                elif typen == 'sum':
                    lineout += "%s;" % sum(OUTs[key][DIR])
            print lineout

if __name__ == '__main__':
    retcont = {}
    retjobs = {}
    retperf = {}
    goodjobs = []
    goodfilter = []
    for DIR in [GOODJOBDIR]:
        path = '%s/%s/' % (MAINDIR, DIR)
        try:
            onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
        except OSError:
            break
        for fname in onlyfiles:
            fileids = fname.split('-')
            goodjobs.append(int(fileids[1]))
    goodfilter = copy.deepcopy(goodjobs)
    for DIR in ALLDIRS:
        path = '%s/%s/' % (MAINDIR, DIR)
        for idg in goodjobs:
            fname = join(path, 'jobrep-%s-0' % idg)
            if not isfile(fname):
                try:
                    goodfilter.remove(idg)
                except ValueError:
                    print 'Already removed'
                print DIR, fname
    print 'overallgood jobs %s %s' % (goodjobs, len(goodjobs))
    print 'goodfilter jobs %s %s ' % (goodfilter, len(goodfilter))
    for DIR in ALLDIRS:
        retcont[DIR], retjobs[DIR], retperf[DIR] = scandir(DIR)
    timingkeys = []
    for DIR in ALLDIRS:
        for key, _vals in retcont[DIR].items():
            if key.endswith('totalMsecs'):
                if key not in timingkeys:
                    timingkeys.append(key)
    #getgraph(timingkeys, retjobs)
    #timingkeys += PERFKEYS
    #printsummary(timingkeys, retjobs, goodjobs)
    #print '-'*100
    #printsummary(PERFKEYS, retperf, goodjobs)
    # -----------------------------------------------------------
    OUTExit = {}
    for jobid in range(1,401):
        if jobid not in goodjobs:
            continue
        for DIR in ALLDIRS:
            OUTExit.setdefault(DIR, {})
            exitCode = 1000
            try:
                exitCode = int(retperf[DIR][str(jobid)]['exitcode'])
            except KeyError:
                exitCode = 1000
            OUTExit[DIR].setdefault(exitCode, 0)
            OUTExit[DIR][exitCode] += 1
    for key, val in OUTExit.items():
        print key, val


    print '-'*100
    getAVGs(PERFKEYS, retperf, goodjobs)
    print '-'*100
    print 'Only Failures'
    getAVGs(PERFKEYS, retperf, goodjobs, True)
    print '-'*100
    getAVGs(PERFKEYS, retperf, goodfilter)
    print '-'*100
    getAVGs(timingkeys, retjobs, goodfilter)
    #getSummaryPerf(PERFKEYS, retperf, goodjobs)
    #getSummaryPerf1(timingkeys, retcont, goodjobs)
