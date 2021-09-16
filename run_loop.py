import os, optparse,sys

#!/usr/bin/env python

datamc = sys.argv[1]
year   = sys.argv[2]
lep    = sys.argv[3]
sample = ''
if (len(sys.argv)>4): sample = sys.argv[4]
cmsenv = ' eval `scramv1 runtime -sh` '
os.system(cmsenv+ ";python loop.py "+ datamc+" "+year+" "+lep+" "+ sample)
