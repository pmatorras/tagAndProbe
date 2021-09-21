#!/usr/bin/env python

import os, optparse,sys

tagPro = "/afs/cern.ch/work/p/pmatorra/private/CMSSW_10_6_19/src/tagAndProbe"
datamc = sys.argv[1]
year   = sys.argv[2]
lep    = sys.argv[3]
sample = ''
if (len(sys.argv)>4): sample = sys.argv[4].split('/')[-1]
cmsenv = ' eval `scramv1 runtime -sh` '
pwd = os.getenv("PWD")
print pwd
os.system("cd "+tagPro+"; "+cmsenv+ "; python loop.py "+ datamc+" "+year+" "+lep+" "+ sample)
