#!/usr/bin/env python                                                                          
import os,sys,optparse
from datetime import datetime
import numpy as np                
import optparse
import sys, os
cmsenv   = ' eval `scramv1 runtime -sh` '
fol_base = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/'


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
    f.write("executable            = "+PWD+"run_loop.py \n")
    f.write("arguments             = "+arguments+jobsent+"\n")
    f.write("output                = "+folder+"/"+sample+"/job.$(Process).out\n")
    f.write("error                 = "+folder+"/"+sample+"/job.$(Process).err\n")
    f.write("log                   = "+folder+"/"+sample+"/job.$(Process).log\n")
    #f.write("+JobFlavour           = nextweek\n")                                             
    f.write("+JobFlavour           = longlunch\n")#testmatch\n")
    #f.write("+JobFlavour           = tomorrow\n")                                             
    f.write("queue "+sample+' from '+fileloc+' \n')
    f.close()

alltypes = ["data", "mc"]
allyears = ["2016", "2017", "2018"]  
allLeps  = ["Ele" , "Muon"]
NLO      = ''
LO       = '' 

if len(sys.argv)<4:
    if "all" in sys.argv[-1]:
        years = allyears 
        leps  = allLeps
        if(len(sys.argv)<3): datamcs = alltypes
        else: datamcs = sys.argv[1] 
    else:
        print 'Please, specify Sample, number of events and file location, in that order'
        sys.exit()
else:
    datamcs = sys.argv[1]
    years   = sys.argv[2]
    leps    = sys.argv[3]

    if "all" in datamcs.lower(): datamcs = alltypes
    else: datamcs = datamcs.split('_')
    if "all" in years.lower()  : years   = allyears
    else: years   = years.split("_")
    if "all" in    leps.lower(): leps    = allLeps
    else: leps    = leps.split("_")
    if len(sys.argv)>4:
        if "nlo" in sys.argv[4]: NLO="NLO"

for datamc in datamcs:
    for year in years:
        yshort    = year.replace("20","")
        if "20" not in year: year = "20"+year
        if "16" in year: 
            hipms = ["_noHIPM", "_HIPM"]
        else: hipms = [""]
        for hipm in hipms:
            for lep in leps:
                if "e" in lep.lower(): lep = "Ele"
                if "m" in lep.lower(): lep = "Muon"
                if "data" in datamc.lower(): 
                    fol_name = fol_base + "Run"+year+"_UL"+year +   "_nAODv8"+hipm+"_Full"+year+"v8/DataTandP__addTnP"+lep+"/"
                elif "mc" in datamc.lower(): 
                    fol_name = fol_base + "Summer20UL"+ yshort+"_106x_nAODv8"+hipm+"_Full"+year+"v8/MCTandP__addTnP"+lep+"/"
                    if 'NLO'  in NLO : LO = "*50__part*"
                    else             : LO = "*LO*"
                arguments   = datamc+" "+year+" "+lep
                sample      = arguments.replace(" ","")+NLO
                jobfolder   = "./Condor"
                logfile     = jobfolder + '/log_'+sample+".log"
                subfilename = jobfolder + '/sub_'+sample+".sub"
                flistname   = jobfolder+'/joblist' +sample+'.txt'
                os.system("mkdir -p "+jobfolder+"/"+sample)
                print os.system("ls "+fol_name+LO), "ls "+ fol_name+LO
                os.system('rm -f '+flistname)
                os.system("ls "+fol_name+LO+">> "+flistname)
                logtitle(logfile,"fileset")
                logline =   "Input arguments:\t"+ arguments 
                logline+= "\nSample list    :\t"+ flistname
                logline+= "\nSubmission file:\t"+ subfilename
                writetolog(logfile, logline)


                makeSubFile2(subfilename,jobfolder, arguments, sample, flistname)# , "fileset","doDC",lognm)  
                commandtorun = "condor_submit "+subfilename+" >> "+logfile


                os.system(commandtorun)
                print "jobs sent:\n", commandtorun
                writetolog(logfile,"----------------------------------")
                print "LIMITS SENT\nlog file:\t"+logfile,"\nsub file:\t"+subfilename,"\njob list:\t"+flistname


