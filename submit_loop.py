#!/usr/bin/env python                                                                          
import os,sys,optparse
from datetime import datetime
import numpy as np                
import optparse
import sys, os
cmsenv = ' eval `scramv1 runtime -sh` '
#optim  = '/afs/cern.ch/work/p/pmatorra/private/CMSSW_10_2_14/src/Optimisecuts/'               

if len(sys.argv)<4:
    print 'Please, specify Sample, number of events and file location, in that order'
    sys.exit()

datamc = sys.argv[1]
year   = sys.argv[2].replace("20","")
lep    = sys.argv[3]
ylong  = "20"+year
fol_name = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/'

if "e" in lep.lower(): lep = "Ele"
if "m" in lep.lower(): lep = "Muon"
if "data" in datamc.lower(): fol_name += "Run"+ylong+"_UL"+ylong+"_nAODv8_Full"+ylong+"v8/DataTandP__addTnP"+lep+"/"
elif "mc" in datamc.lower(): fol_name += "Summer20UL"+year+"_106x_nAODv8_Full"+ylong+"v8/MCTandP__addTnP"+lep+"/"



#write header to logfile                                                                       
def logtitle(filename,sigset):
    if(os.path.exists(filename) is False):  print "creating log file"
    f = open(filename,"a")
    # Textual month, day and year                                                              
    now = datetime.now()
    d2  = now.strftime("%d %B, %Y, at %H:%M:%S")
    f.write(d2+"\nTAG AND PROBE FOR:\t "+ sigset+"\n")
    f.close()
#Create log file                                                                               
def writetolog(filename,line):
    f = open(filename,"a")
    f.write(line+'\n')
    f.close()
    #print "line", line 


def makeSubFile2(filename,folder,arguments, sample, fileloc):#year,tag,sigset,fileset, doDC,writesigset):
    PWD = os.getenv('PWD')+'/'
    f = open(filename,"w+")
    jobsent   = ' $(' +sample+ ')'
    #print "creating "+filename+" \t ARGUMENTS:\n ",arguments, "\n"                            
    f.write("executable            = "+PWD+"loop.py \n")
    f.write("arguments             = "+arguments+jobsent+"\n")
    f.write("output                = "+folder+"/"+sample+"/job.$(Process).out\n")
    f.write("error                 = "+folder+"/"+sample+"/job.$(Process).err\n")
    f.write("log                   = "+folder+"/"+sample+"/job.$(Process).log\n")
    #f.write("+JobFlavour           = nextweek\n")                                             
    f.write("+JobFlavour           = longlunch\n")#testmatch\n")
    #f.write("+JobFlavour           = tomorrow\n")                                             
    f.write("queue "+sample+' from '+fileloc+' \n')
    f.close()


arguments   = datamc+" "+year+" "+lep
sample      = arguments.replace(" ","")
jobfolder   = "./Condor"
logfile     = jobfolder + '/log_'+sample+".log"
subfilename = jobfolder + '/sub_'+sample+".sub"
flistname   = jobfolder+'/joblist' +sample+'.txt'

os.system("ls "+fol_name+">> "+flistname)
os.system("mkdir -p "+jobfolder+"/"+sample)
logtitle(logfile,"fileset")
logline =   "Input arguments:\t"+ arguments 
logline+= "\nSample list    :\t"+ flistname
logline+= "\nSubmission file:\t"+ subfilename
writetolog(logfile, logline)


makeSubFile2(subfilename,jobfolder, arguments, sample, flistname)# , "fileset","doDC",lognm)  
commandtorun = "condor_submit "+subfilename+">>"+logfile


os.system(commandtorun)
print "jobs sent:\n", commandtorun
writetolog(logfile,"----------------------------------")
print "LIMITS SENT\nlog file:\t"+logfile,"\nsub file:\t"+subfilename,"\njob list:\t"+flistname


