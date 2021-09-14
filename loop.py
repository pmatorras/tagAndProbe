from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TLegend, gDirectory, TTree


#!/usr/bin/env python                                                                   
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
fol_name = ''

if "e" in lep.lower(): lep = "Ele"
if "m" in lep.lower(): lep = "Muon"
if "data" in datamc.lower(): fol_name = "Run"+ylong+"_UL"+ylong+"_nAODv8_Full"+ylong+"v8/DataTandP__addTnP"+lep+"/"
elif "mc" in datamc.lower(): fol_name = "Summer20UL"+year+"_106x_nAODv8_Full"+ylong+"v8/MCTandP__addTnP"+lep+"/"
if len(sys.argv)==4 :
    if "data" in datamc.lower():
        if lep is "Ele": hfilenm  = fol_name+ "nanoLatino_SingleElectron_Run2017B-UL2017-v1__part0.root"
        else: hfilenm = fol_name+"nanoLatino_SingleMuon_Run2017B-UL2017-v1__part0.root"

    else:
        hfilenm = fol_name+"nanoLatino_DYJetsToLL_M-50_LO__part0.root"
else :
    hfilenm  = fol_name+sys.argv[4]

print fol_name, hfilenm
hfile   = TFile(hfilenm,"READ","Example");

events = hfile.Get("Events")
nEntries =  10000#events.GetEntries()
#nEntries =  events.GetEntries()

ptcut    = 20
if lep is "Muon": ptcut=15
etacut   = 2.4
sip3Dcut = 4
dxycut   = 0.05
dzcut    = 0.1
Ncutb    = 0
Nallcuts = 0
#print events.Scan("Probe_lostHits")
for i in range(0, nEntries):
    #print events.HLT_PFJet200
    events.GetEntry(i)
    lep_pt    = events.Probe_pt
    lep_eta   = events.Probe_eta
    lep_sip3D = events.Probe_sip3d
    lep_dxy   = events.Probe_dxy
    lep_dz    = events.Probe_dz
    if   lep is "Ele" :
        lep_cut  = events.Probe_cutBased
        if lep_cut  < 3:                               continue
    elif lep is "Muon":
        lep_cut  = events.Probe_mediumId
        if lep_cut !=1: continue
    Ncutb    += 1

    #print lep_pt, lep_eta, lep_dxy, lep_dz, lep_sip3D, lep_lostH, lep_cutB

    if lep_pt    < ptcut  or abs(lep_eta) > etacut: continue
    if lep_dxy   > dxycut or lep_dz       > dzcut : continue
    if lep_sip3D < sip3Dcut:                        continue

    if lep is "Ele":
        eveHit = -1
        if   lep_pt == events.Electron_pt[0] : eveHit = 0
        elif lep_pt == events.Electron_pt[1] : eveHit = 1
        lep_lostH = events.Electron_lostHits[eveHit]
        
        if lep_lostH != 0 :                      continue
    elif lep is "Muon":
        if events.Probe_miniPFRelIso_all > 0.15: continue

    Nallcuts += 1
    #print i,":", events.event,
    #print lep_pt, lep_eta, lep_dxy, lep_dz, lep_sip3D, lep_cut
    #print events.Probe_miniPFRelIso_all

print "Cut based:\t",Ncutb,"\nAll cuts:\t",Nallcuts
