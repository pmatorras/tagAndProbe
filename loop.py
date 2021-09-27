from ROOT import TCanvas, TPad, TFile, TPaveLabel, TPaveText, TLegend, gDirectory, TTree, TH2D, TH1D
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection

print "starting the code"
#!/usr/bin/env python       
import optparse
import sys, os
import numpy as np



cmsenv = ' eval `scramv1 runtime -sh` '
user   = os.getenv("USER")
xEdges = np.array([ -2.5, -2.0, -1.566, -1.444, -0.8, 0.0, 0.8, 1.444, 1.566, 2.0, 2.5], dtype = 'double')
yEdges = np.array([   10,   20,     35,     50,  100, 200], dtype ='double')
nbinX  = len(xEdges)-1
nbinY  = len(yEdges)-1
hipms  = ["_noHIPM", "_HIPM"]

if "pablinux" in user:
    fol_name = ""
else:
    fol_name = '/eos/cms/store/group/phys_higgs/cmshww/amassiro/HWWNano/'
    os.system(cmsenv)



if len(sys.argv)<4:
    print 'Please, specify Sample, number of events and file location, in that order'
    sys.exit()

datamc = sys.argv[1]
year   = "20"+sys.argv[2].replace("20","")
lep    = sys.argv[3]
hipm   = ''
if "16" in year:
    if "noHIPM" in year: 
        hipm = "_noHIPM"
        year = year.replace("_noHIPM", "")
    else:                
        hipm = "_HIPM"
        year = year.replace("_HIPM", "")

yshort   = year.replace("20","")

if   "e" in lep.lower(): lep = "Ele"
elif "m" in lep.lower(): lep = "Muon"
else: 
    print "wrong lepton input\n exiting"
    exit()

if len(sys.argv)==4 :
    if "data" in datamc.lower():
        if lep is "Ele": samplenm  = "nanoLatino_SingleElectron_Run"+year+"B-UL"+year+"-v1__part0.root"
        else:            samplenm  = "nanoLatino_SingleMuon_Run"+year+"B-UL"+year+"-v1__part0.root"

    else:
        if "16" in year: samplenm = "nanoLatino_DYJetsToLL_M-50-LO__part0.root"
        else           : samplenm = "nanoLatino_DYJetsToLL_M-50_LO__part0.root"
else :
    samplenm  = sys.argv[4]

if "data" in datamc.lower() : fol_name += "Run"+year+"_UL"+year+"_nAODv8"+hipm+"_Full"+year+"v8/DataTandP__addTnP"+lep+"/"
elif "mc" in datamc.lower() : fol_name += "Summer20UL"+yshort+"_106x_nAODv8"+hipm+"_Full"+year+"v8/MCTandP__addTnP"+lep+"/"
elif "data" not in datamc.lower() and "mc" not in datamc.lower():
    print "pick either data or mc\n exiting"
    exit()

print "arguments", datamc, year, lep
NLOstr    = 'LO'
isNLO     = False
all_syst  = {"Ele"  : {"tagEle"  : "mvaFall17V2Iso_WP90"}, # To be added "NLO": "NLO"},
             "Muon" : {"tagMu1"  : 0.1,"tagMu3"   : 0.3, "TnP_m1": [75,140], "TnP_m2" : [65,120]},
             "Both" : {"central" : "" ,"TnP_MET30": 30 , "TnP_MET50" : 50, "nojet" : 0}}
jetlcuts  = {"2016_HIPM" : 0.2027 , "2016_noHIPM": 0.1918, "2017" : 0.1355, "2018":0.1208}
jetlcut   = jetlcuts[year+hipm]
if "16" in year:
    apv = 'APV'
    if "NOHIPM" in year: apv=''
    PUweights = np.loadtxt("PUfiles/PileUpWeights_DiJet20_QCDMu_PSRun2016UL16"+apv+".txt", comments="#", delimiter=" ", unpack=False)
else:
    PUweights = np.loadtxt("PUfiles/PileUpWeights_DiJet20_QCDMu_PSRun"+year+"UL"+yshort+".txt", comments="#", delimiter=" ", unpack=False)
lep_syst  = dict(all_syst[lep], **all_syst["Both"])

if "mc" in datamc.lower() and "LO_" not in samplenm: 
    isNLO    = True
    lep_syst = {"centralNLO" :""}
    NLOstr   = "NLO"
sample    =  datamc+year+lep
sampleloc = fol_name+samplenm
outputfol = "Output/"+sample+NLOstr+hipm
outputnm  = outputfol+"/output_"+samplenm
print " sample ",sampleloc, "being used"
os.system("mkdir -p "+outputfol) 
hsample   = TFile(sampleloc,"READ","input_file")
foutput   = TFile(outputnm, "RECREATE", "output_file")
events    = hsample.Get("Events")
#nEntries  = 1000
nEntries  =  events.GetEntries()
ptcut     = 20
if lep is "Muon": ptcut = 15
etacut    = 2.4
sip3Dcut  = 4
dxycut    = 0.05
dzcut     = 0.1
for syst in lep_syst:
    if lep is "Muon":
        lepnm    = lep
        if "TnP_m" in syst:
            min_mass = lep_syst[syst][0]
            max_mass = lep_syst[syst][1]
        else:
            min_mass =  70
            max_mass = 130
    else:
        lepnm    = "Electron"
        min_mass =  60
        max_mass = 120

    Ncutb     = 0
    Nallcuts  = 0
    hbasecuts = TH2D(sample+"base" +syst, sample+"base cuts, "  +syst,  nbinX, xEdges, nbinY, yEdges)
    hallcuts  = TH2D(sample+"all"  +syst, sample+"all cuts, "   +syst,  nbinX, xEdges, nbinY, yEdges)
    hbasemass = TH1D(sample+"baseM"+syst, sample+"base cuts M, "+syst,  40, min_mass, max_mass)
    hallmass  = TH1D(sample+"allM" +syst, sample+"all cuts M, " +syst,  40, min_mass, max_mass)

    print "considering syst", syst, ":",lep_syst[syst]
    for i in range(0, nEntries):
        #print events.HLT_PFJet200
        events.GetEntry(i)
        leptons = Collection(events, lepnm)
        if lep is "Muon": nlep = events.nMuon
        else:             nlep = events.nElectron

        #pick which lep is the corresponding to probe
        eveHit    = -1
        for ilep in range(0,nlep):
            if leptons[ilep].pt == events.Probe_pt: eveHit = ilep
        if eveHit == -1:
            print "no match, continue"
            continue

        lep_pt    = leptons[eveHit].pt
        lep_pt    = leptons[eveHit].pt
        lep_eta   = leptons[eveHit].eta
        lep_sip3D = leptons[eveHit].sip3d
        lep_dxy   = leptons[eveHit].dxy
        lep_dz    = leptons[eveHit].dz
        tnp_mass  = events.TnP_mass

        if   lep is "Ele" :
            lep_cut  = events.Probe_cutBased
            if lep_cut < 3 : continue
        elif lep is "Muon" :
            lep_cut  = leptons[eveHit].mediumId
            if lep_cut !=1                            : continue
            if leptons[eveHit].miniPFRelIso_all > 0.15: continue
            if leptons[eveHit].pfRelIso04_all   > 0.2 : continue

        if len([x for x in events.Jet_btagDeepB if x > jetlcut])>0: continue
        if events.TnP_trigger ==0:                                  continue
        if tnp_mass< min_mass or tnp_mass>max_mass:                 continue
        
        if "MET"   in syst and events.TnP_met>lep_syst[syst]                 : continue
        if "WP90"  in syst and leptons[eveHit].mvaFall17V2Iso_WP90<1         : continue
        if "nojet" in syst and leptons[eveHit].jetIdx <1                     : continue
        if "tagMu" in syst and leptons[eveHit].pfRelIso04_all>lep_syst[syst] : continue

        Ncutb    += 1
        if "mc" in datamc: weight = PUweights[int(events.Pileup_nTrueInt),1]
        else             : weight = 1
        hbasecuts.Fill(lep_eta, lep_pt,weight)
        hbasemass.Fill(tnp_mass, weight)
        
        #print lep_pt, lep_eta, lep_dxy, lep_dz, lep_sip3D#, lep_lostH, lep_cutB

        if lep_pt    < ptcut  or abs(lep_eta) > etacut: continue
        if lep_dxy   > dxycut or lep_dz       > dzcut : continue
        if lep_sip3D < sip3Dcut:                        continue
        if lep is "Ele":
            lep_lostH = leptons[eveHit].lostHits
            if lep_lostH != 0 :                      continue
        Nallcuts += 1
        hallcuts.Fill(lep_eta, lep_pt,weight)
        hallmass.Fill(tnp_mass, weight)
        
    print "Cut based:\t",Ncutb,"\nAll cuts:\t",Nallcuts
    
    hbasecuts.Write()
    hbasemass.Write()
    hallcuts.Write()
    hallmass.Write()
    
print "finished..."
