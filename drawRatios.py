from        loop import *
from submit_loop import *
from        ROOT import gStyle, gROOT, TColor, TAxis
from       array import array
gStyle.SetOptStat(0);
gROOT.SetBatch(True)
gStyle.SetPaintTextFormat("4.3f");
NRGBs  = 5
maxerr = 0.2 
NCont  = 255
stops  = array("d",[0.00, 0.34, 0.61, 0.84, 1.00])
red    = array("d",[0.50, 0.50, 1.00, 1.00, 1.00])
green  = array("d",[ 0.50, 1.00, 1.00, 0.60, 0.50])
blue   = array("d",[1.00, 1.00, 0.50, 0.40, 0.50])
TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
gStyle.SetNumberContours(NCont)

def getEdges(lep):
    if "Ele" in  lep:
        xedges = np.array([ -2.5, -2.0, -1.566, -1.444, -0.8, 0.0, 0.8, 1.444, 1.566, 2.0, 2.5], dtype = 'double')
        yedges = np.array([   10,   20,     35,     50,  100, 200], dtype ='double')
    elif "Muon" in lep:
        xedges = np.array([ -2.4, -2.1, -0.9, 0, 0.9, 2.1, 2.4], dtype = "double")
        yedges = np.array([ 15, 20, 25, 30, 40, 50, 60, 120], dtype="double")
    else:
        print "not the write lep", lep
        exit()
    return xedges, yedges



def getEff_i(heff, hbase, i,j, isMC=False):
    val_i = heff.GetBinContent(i,j)
    if heff.GetBinContent(i,j) >0:
        err_i = np.sqrt(heff.GetBinContent(i,j)*(1-heff.GetBinContent(i,j))/(hbase.GetBinContent(i,j)))
    else: 
        err_i = 0
    return val_i,err_i

def sethistos(histo, year,plot_type, subtype, labels, folder, datamc):
    plottext = "colztext" 
    lep      = "Muon"
    if "Electron"   in labels   : lep  = "Electron"
    titleextra = " "+lep
    if "eff"        in plot_type: titleextra  = "allcuts/basecuts" + titleextra
    if "DataMC" not in datamc   : titleextra += " ("+datamc+")" 
    if "Mass"   not in subtype  : 
        histo.GetYaxis().SetRangeUser(20,200)
        if plot_type== "SF"  and "err" not in subtype:
            histo.SetMinimum(0.9)
            histo.SetMaximum(1.05)
        elif "eff" in plot_type:
            histo.SetMinimum(0.0)
            histo.SetMaximum(1.4)
    if plot_type == "SF" or "cen" in subtype: 
        histo.SetTitle(labels)
        
    else:
        histo.SetTitle(year+" "+plot_type+" "+subtype+" "+titleextra+labels)
    if (plot_type == "SF" and "cen" in subtype) or 'eff' in plot_type: plottext+="e"
    print plottext, plot_type
    #exit()
    histo.Draw(plottext)
    figname= plot_type+"_"+subtype.replace(" ","")+"_"+datamc+".png"
    c1.SaveAs(folder+lep+"_"+figname)
    if "SF_cen" in figname:
        for i in range(1,nbinX+1):
            for j in range(8,nbinY+1):
                print "what's this",labels, i,j,histo.GetBinContent(i,j), histo.GetBinError(i,j)
    histo.Write()
    

if __name__ == '__main__':
    
    if len(sys.argv)>3:
       datamcs, years, leps, NLO = getinputs()
    else:
        years = ["2018"]
        leps  = ["Ele"]
    print "Making plots for", years, leps
    #confirm()

    c1 = TCanvas( 'c1', 'Ratio plot', 200,10, 1600, 900 )
    c1.SetLogy()

    for year in years:
        hipms = addHipm(year)
        for hipm in hipms:
            folbase   = 'Histograms/'+year+hipm+'/'
            print year, hipm
            for lep in leps:
                #define several interesting variables
                nbinXhist = len(xEdges[lep])-1
                nbinYhist = len(yEdges[lep])-1
                #different numbering to take the overflow into account
                nbinX     = nbinXhist
                nbinY     = nbinYhist+1 #different since here we're taking overflow here

                lepstr    = lep+" "
                if "Ele" in lep: lepstr = "Electron"+" "
                lep_syst  = dict(all_syst[lep], **all_syst["Both"])
                lep_syst["centralNLO"] = "centralNLO"
                sample    = year+lep
                samplenm  = year+hipm+lep
                samplefol = "Output/hadd/"
                outputnm  = samplefol+"AdditionalSF_"+samplenm+".root"
                sampleloc = samplefol+"merge_"+samplenm+".root"
                hsample   = TFile(sampleloc,"READ","input_file")
                foutput   = TFile(outputnm, "RECREATE", "output_file")
                hbasecuts      = TH2D(sample+"base" , sample+"base cuts, ",  nbinXhist, xEdges[lep], nbinYhist, yEdges[lep])
                hSFstaterr     = TH2D("hSFstaterr"+lep, sample+"staterr, ",  nbinXhist, xEdges[lep], nbinYhist, yEdges[lep])
                hSFsysterr     = TH2D("hSFsysterr"+lep, sample+"systerr, ",  nbinXhist, xEdges[lep], nbinYhist, yEdges[lep])
                hSFerr         = TH2D("hSFerr"    +lep, sample+"err, "    ,  nbinXhist, xEdges[lep], nbinYhist, yEdges[lep])
                hbaseData_cen  =  hsample.Get("data"+sample+"basecentral")
                hallData_cen   =  hsample.Get("data"+sample+"allcentral")
                hbaseMC_cen    =  hsample.Get(  "mc"+sample+"basecentral")
                hallMC_cen     =  hsample.Get(  "mc"+sample+"allcentral")
                heffData_cen   =  hallData_cen.Clone("heffDatacentral")
                heffMC_cen     =  hallMC_cen.Clone("heffMCcentral")
                done_tnpmass   = False
                done_muontag   = False
                heffData_cen.Divide(hbaseData_cen)
                heffMC_cen.Divide(hbaseMC_cen)
                hSFDataMC_cen  = heffData_cen.Clone("hSFDataMC_central")
                hSFDataMC_cen.Divide(heffMC_cen)
                print nbinX, xEdges[lep], yEdges[lep]
                #exit()
                for syst in lep_syst:
                    if "Muon" in lep and "NLO" in syst: continue
                    hfolder   = folbase+syst+'/'
                    os.system("mkdir -p "+hfolder)
                    #if "nojet" not in syst: continue
                    print "DOING SYSTEMATIC",syst
                    systD =syst
                    if "NLO" in syst: 
                        continue
                        systD = 'central' 
                    for M in ["","M"]:
                        hbaseData  =  hsample.Get("data"+sample+"base"+M+systD)
                        hallData   =  hsample.Get("data"+sample+"all" +M+systD)
                        hbaseMC    =  hsample.Get(  "mc"+sample+"base"+M+syst)
                        hallMC     =  hsample.Get(  "mc"+sample+"all" +M+syst)
                        
                        #print  "getting", hallData, "data"+sample+"base"+M+systD
                        heffData   =  hallData.Clone("heffData" +M+syst)
                        heffMC     =  hallMC.Clone("heffMC" +M+syst)

                        hist_type = "colz text"
                        labels    = ";#eta;"+lepstr+"p_{T}"
                        Mstr      = ''
                        heffData.Divide(hbaseData)
                        heffMC.Divide(hbaseMC)
                        if "M" in M: 
                            hist_type = ''
                            labels    = syst+" Mass ;"+lepstr+"p_{T}"
                            Mstr      = "_Mass"
                            sethistos(heffData, year,"eff", syst+Mstr, labels,hfolder, "Data")
                            sethistos(heffMC  , year,"eff", syst+Mstr, labels,hfolder, "MC")
                            continue
                        #search for efficiencies where there's not much data
                        for i in range(1,nbinX+1):
                            for j in range(1, nbinY+1):
                                #print i, j
                                rbaseDataij = 1/hbaseData.GetBinContent(i,j) if hbaseData.GetBinContent(i,j)>0 else 0
                                rallDataij  = 1/hallData.GetBinContent(i,j)  if hallData.GetBinContent(i,j)>0  else 0
                                rbaseMCij   = 1/hbaseMC.GetBinContent(i,j)   if hbaseMC.GetBinContent(i,j)>0   else 0
                                rallMCij    = 1/hallMC.GetBinContent(i,j)    if hallMC.GetBinContent(i,j)>0    else 0
                                erreffData = heffData.GetBinContent(i,j)*np.sqrt(rbaseDataij+rallDataij)
                                erreffMC   = heffMC.GetBinContent(i,j)  *np.sqrt(rbaseMCij  +rallMCij  )
                                heffData.SetBinError(i,j,erreffData)
                                heffMC.  SetBinError(i,j,erreffMC  )
                                #if j==8: print "my checks",  nbinX, nbinY, i, j, heffData.GetBinContent(i,j), erreffData, 1/rbaseDataij, 1/rallDataij  
                        sethistos(heffData, year,"eff", syst+Mstr, labels,hfolder, "Data")
                        sethistos(heffMC  , year,"eff", syst+Mstr, labels,hfolder, "MC")

                        if syst != "central":
                            hSFDataMC  = heffData.Clone("hSFDataMC"+syst)
                            hSFDataMC.Divide(heffMC)
                            sethistos(hSFDataMC, year,"SF"+syst, Mstr, labels,hfolder, "DataMC")
                            heffDataerr = heffData.Clone(year+"heffDataerr" +M+syst)
                            heffMCerr   = heffMC.Clone(  year+"heffMCerr"   +M+syst)
                        
                        #make sure the systematics are properly taken
                        if "MET50" in syst: continue
                        passeschecks = False
                        if (done_muontag and "tagMu" in syst) or (done_tnpmass and "TnP_m" in syst):
                            passeschecks = True
                            if   "TnP_m" in syst: othersyst = othersystmass
                            elif "tagMu" in syst: othersyst = othersystMtag
                            else:
                                print "something is wrong, check it out"
                                exit()

                        #stack different parts together to get the SF
                        for i in range(1,nbinX + 1):
                            for j in range(1,nbinY + 1):
    
                                allerr_iSF  = hSFerr.GetBinContent(i,j)
                                if "central" in syst and "NLO" not in syst:
                                    val_iMC  , err_iMC   = getEff_i(heffMC,hbaseMC, i,j, True)
                                    val_iData, err_iData = getEff_i(heffData,hbaseData,i,j)
                                    if val_iMC <1e-9 and val_iData <1e-9: err_SF = 0
                                    else:
                                        if val_iMC   < 1e-9: val_iMC   = 1e9
                                        if val_iData < 1e-9: val_iData = 1e9
                                        err_SF = np.sqrt((err_iMC/val_iMC)**2+(err_iData/val_iData)**2)
                                    allstat_iSF = hSFstaterr.GetBinContent(i,j)
                                    hSFstaterr.SetBinContent(i,j, allstat_iSF+err_SF)
                                else:
                                    central_iSF = hSFDataMC_cen.GetBinContent(i,j)
                                    syst_iSF    = hSFDataMC.GetBinContent(i,j)
                                    syst_allSF  = hSFsysterr.GetBinContent(i,j)
                                    if syst_iSF>0: syst_idiff  = (central_iSF-syst_iSF)**2
                                    else         : syst_idiff  = 0
                                    
                                    if "tagMu" in syst or "TnP_m" in syst:
                                        if passeschecks:
                                            otherSF     = foutput.Get("hSFDataMC"+M+othersyst)
                                            other_idiff = (central_iSF-otherSF.GetBinContent(i,j))**2
                                            syst_idiff  =  max(syst_idiff, other_idiff)
                                        else: 
                                            syst_idiff  = 0
                                    
                                    if  heffData.GetBinError(i,j)>maxerr or heffMC.GetBinError(i,j)>maxerr:
                                        print "Hello",i,j, heffData.GetBinContent(i,j), heffData.GetBinError(i,j), heffMC.GetBinError(i,j)

                                    else:
                                        hSFsysterr.SetBinContent(i,j,syst_allSF+syst_idiff)
                    
                    if "TnP_m" in syst: 
                        done_tnpmass  = True
                        othersystmass = "TnP_m"+syst[-1]
                    if "tagMu" in syst: 
                        done_muontag  = True
                        othersystMtag = "tagMu"+syst[-1]
                #do the rest
                labels   =";#eta;"+lepstr+"p_{T}"
                fcentral = folbase+"central/"
                for i in range(1,nbinX + 1):
                    for j in range(1,nbinY + 1):
                        allsysterrsq_i = hSFsysterr.GetBinContent(i,j)
                        allstaterr_i   = hSFstaterr.GetBinContent(i,j)
                        allerr_i       = np.sqrt(allsysterrsq_i+allstaterr_i**2)
                        hSFerr.SetBinContent(i,j, allerr_i)
                        hSFDataMC_cen.SetBinError(i,j, allerr_i)
                        if j>5: print j, i, allerr_i, hSFDataMC_cen.GetBinError(i,j)
                        
                hSFDataMC_cen.SetMinimum(0.9)
                hSFDataMC_cen.SetMaximum(1.05)
                
                
                sethistos(hSFDataMC_cen, year,"SF", "cen"     , labels,fcentral, "DataMC")                    
                sethistos(hSFsysterr   , year,"SF", "syst err", labels,fcentral, "DataMC")
                sethistos(hSFstaterr   , year,"SF", "stat err", labels,fcentral, "DataMC")
                sethistos(hSFerr       , year,"SF", "err"     , labels,fcentral, "DataMC")
                                
                                
    #exit()

    print "All systematics processed, now saving it to the web..."
    www = os.getenv('WWW')
    wloc = www+'/susy/tagAndProbe'
    os.system('mkdir -p '+wloc)
    os.system('cp -r Histograms '+wloc)
    os.system('cp '+www+'/susy/V9_Plots/index.php '+wloc+"/Histograms/")
    for year in years:
        hipms = addHipm(year)
        for hipm in hipms:
            for lep in leps:
                lep_syst  = dict(all_syst[lep], **all_syst["Both"])
                for syst in lep_syst:
                    print year, hipm, syst
                    os.system('cp '+www+'/susy/V9_Plots/index.php '+wloc+"/Histograms/"+year+hipm+"/")
                    os.system('cp '+www+'/susy/V9_Plots/index.php '+wloc+"/Histograms/"+year+hipm+"/"+syst+"/")###
    
