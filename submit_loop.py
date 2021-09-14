#!/usr/bin/env python                                                                          
import os,sys,optparse
from datetime import datetime
import numpy as np


nMPs        = 1


#write header to logfile                                                                       
def logtitle(filename,sigset):
    if(os.path.exists(filename) is False):  print "creating log file"
    f = open(filename,"a")
    # Textual month, day and year                                                              
    now = datetime.now()
    d2  = now.strftime("%d %B, %Y, at %H:%M:%S")
    f.write(d2+"\nCALCULATING LIMITS FOR:\t "+ sigset+"\n")
    f.close()
#Create log file                                                                               
def writetolog(filename,line):
    f = open(filename,"a")
    f.write(line+'\n')
    f.close()
    #print "line", line 


def makeSubFile2(filename,folder,sample, nsample, fileloc, ofilenm):#year,tag,sigset,fileset, doDC,writesigset):
    PWD = os.getenv('PWD')+'/'
    f = open(filename,"w+")
    jobsent= '$(' +sample + ')'
    arguments = sample+' '+nsample+' '+ ' '+jobsent+ ' ' + ofilenm+"_$(Process).root" #+PWD+' '+fileset+' '+str(doDC)
    #print "creating "+filename+" \t ARGUMENTS:\n ",arguments, "\n"                            
    f.write("executable            = "+PWD+"run_loop.py \n")
    f.write("arguments             = "+arguments+"\n")
    f.write("output                = "+folder+"/"+sample+"/job.$(Process).out\n")
    f.write("error                 = "+folder+"/"+sample+"/job.$(Process).err\n")
    f.write("log                   = "+folder+"/"+sample+"/job.$(Process).log\n")
    #f.write("+JobFlavour           = nextweek\n")                                             
    f.write("+JobFlavour           = longlunch\n")#testmatch\n")
    #f.write("+JobFlavour           = tomorrow\n")                                             
    f.write("queue "+sample+' from '+fileloc+' \n')
    f.close()

def getsamples(sample):
    loc=''
    signal={'T2tt': ["T2tt"]}
    samcond=[]
    bkgs={'ttbar': ["TTTo"],'WW': ["_WWTo"],'ttZ':["TTZTo"], 'ZZ': ['_ZZTo','ZZ2']}

    #Check which directory to look at
    bkgloc  = '/eos/cms/store/user/scodella/SUSY/Nano/Summer16_102X_nAODv6_Full2016v6/MCSusy2016v6__MCCorr2016Susyv6__susyMT2/'
    sigloc = '/eos/user/s/scodella/SUSY/Nano/Summer16FS_102X_nAODv4_Full2016v4/susyGen__susyW__MCSusy2016FS__MCCorr2016SusyFS__susyMT2FS/'
    if sample in signal: 
        loc=sigloc
        samcond=signal['T2tt']
    for bkg in bkgs:
        if sample in bkg: 
            loc=bkgloc
            samcond=bkgs[bkg]
    n=3
    #Get all the files in folder for given sample
    allfiles=os.listdir(loc)
    samfiles={}
    flist    = open(flistname,"w+")
    for idx,entry in enumerate(allfiles):
        if(".root" not in entry): continue
        skip=True
        for cond in samcond:
            if cond in entry: skip=False
        if(skip is True): continue
        samfiles[sample+str(idx)]=entry
        
        #if(n
        flist.write(loc+entry+'\n')
    flist.close()
    return samfiles

sfile=None
nSam=1000000
sample=None
#ofile ="Output/postcuts"+sample+".root"

if(len(sys.argv)>1):
    sample=sys.argv[1]
    if(len(sys.argv)>2):
        nSam=sys.argv[2]
        if(len(sys.argv)>3):
            sfile=sys.argv[3]
            if(len(sys.argv)>4):
                ofilenm=sys.argv[4]
print sample
if sample is None: 
    print "please input a sample"
    exit()
#divide masspoints in sets of nMPs and send jobs                                                                
lognm       = sample
jobfolder   = "./Condor"
logfile     = jobfolder + '/log_'+lognm+".log"
subfilename = jobfolder + '/sub_'+lognm+".sub"
flistname   = jobfolder+'/joblist' +lognm+'.txt'

os.system("mkdir -p "+jobfolder+"/"+sample)
logtitle(logfile,"fileset")
logline =   "Input arguments:\t"+ sample + ' ' + str(nSam)
logline+= "\nSample list    :\t" + flistname
logline+= "\nSubmission file:\t"+ subfilename
writetolog(logfile, logline)
ofilenm="Output/cuts"+sample

nfiles=3
if(sample is not None and sfile is None):  sfile=getsamples(sample)
#print sfile
makeSubFile2(subfilename,jobfolder, sample, str(nSam), flistname, ofilenm)# , "fileset","doDC",lognm)  
commandtorun="condor_submit "+subfilename+">>"+logfile


os.system(commandtorun)
print "jobs sent:\n", commandtorun
writetolog(logfile,"----------------------------------")
print "LIMITS SENT\nlog file:\t"+logfile,"\nsub file:\t"+subfilename,"\njob list:\t"+flistname


