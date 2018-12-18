#!/usr/bin/env python

# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
#
# Leopold Haimberger, Dec 2015
#
# Functionality provided: This script triggers the flex_extract test suite. Call with
# testsuite.py [test group]
#
#
# Further documentation may be obtained from www.flexpart.eu
#
# Test groups are specified in testsuite.json
# in addition to a standard python 2.6 or 2.7 installation the following packages need to be installed
# ECMWF WebMARS, gribAPI with python enabled, emoslib, ecaccess web toolkit, all available from https://software.ecmwf.int/
# dateutils
# matplotlib (optional, for debugging)

import os,sys
import json
import subprocess
try:
    taskfile=open('testsuite.json')
except:
    print 'could not open suite definition file testsuite.json'
    exit()

if not os.path.isfile('../src/CONVERT2'):
    print '../src/CONVERT2 could not be found'
    print 'please run "install.py --target=local" first'
    exit()

fprs=os.getenv('FLEXPART_ROOT_SCRIPTS')
if fprs is None:
    print 'FLEXPART_ROOT_SCRIPTS not set .. some test jobs may fail'

tasks=json.load(taskfile,encoding='latin-1')
taskfile.close()
if not os.path.exists('../test'):
    os.makedirs('../test')
if len(sys.argv)>1:
    groups=sys.argv[1:]
else:
    groups=['install','default','ops','work','cv','fc','hireseta','highresgauss','opsfc']
jobcounter=0
jobfailed=0
for g in groups:
    try:
        tk,tv=g,tasks[g]
    except:
        continue
    garglist=[]
    for ttk,ttv in tv.iteritems():
        if isinstance(ttv,basestring):
            if ttk!='script':
                garglist.append('--'+ttk)
                if '$'==ttv[0]:
                    garglist.append(os.path.expandvars(ttv))
                else:
                    garglist.append(ttv)
    for ttk,ttv in tv.iteritems():
        if isinstance(ttv,dict):
            arglist=[]
            for tttk,tttv in ttv.iteritems():
                if isinstance(tttv,basestring):
                    arglist.append('--'+tttk)
                    if '$' in tttv[0]:
                        arglist.append(os.path.expandvars(tttv))
                    else:
                        arglist.append(tttv)
            print 'Command: ',' '.join([tv['script']]+garglist+arglist)
            o='../test/'+tk+'_'+ttk+'_'+'_'.join(ttv.keys())
            print 'Output will be sent to ',o
            f=open(o,'w')
            try:
                p=subprocess.check_call([tv['script']]+garglist+arglist,stdout=f,stderr=f)
            except:
                f.write('\nFAILED\n')
                print 'FAILED'
                jobfailed+=1
            jobcounter+=1
            f.close()

print 'Test suite tasks completed'
print str(jobcounter-jobfailed)+' successful, '+str(jobfailed)+' failed'
print 'If tasks have been submitted via ECACCESS please check emails'
