from        loop import *
from submit_loop import *
from        ROOT import gROOT, gStyle
from       array import array
gStyle.SetOptStat(0);
gROOT.SetBatch(True)
gStyle.SetPaintTextFormat("4.3f");
NRGBs = 5
NCont = 255
stops = array("d",[0.00, 0.34, 0.61, 0.84, 1.00])
red = array("d",[0.50, 0.50, 1.00, 1.00, 1.00])
green = array("d",[ 0.50, 1.00, 1.00, 0.60, 0.50])
blue = array("d",[1.00, 1.00, 0.50, 0.40, 0.50])
ROOT.TColor.CreateGradientColorTable(NRGBs, stops, red, green, blue, NCont)
ROOT.gStyle.SetNumberContours(NCont)

def getEff_i(heff, hbase, i,j, isMC=False):
    val_i = heff.GetBinContent(i,j)
    if heff.GetBinContent(i,j) >0:
        err_i = np.sqrt(heff.GetBinContent(i,j)*(1-heff.GetBinContent(i,j))/(hbase.GetBinContent(i,j)))
    else: 
        err_i = 0
    return val_i,err_i
                        

if __name__ == '__main__':
    
    if len(sys.argv)>3:
       datamcs, years, leps, NLO = getinputs()
    else:
        years = ["2018"]
        leps  = ["Ele"]
        
    
    print "Making plots for", years, leps
    #confirm()

    c1 = TCanvas( 'c1', 'Ratio plot', 200,10, 1600, 900 )
    for year in years:
        hipms = addHipm(year)
        for hipm in hipms:
            folbase   = 'Histograms/'+year+hipm+'/'
            print year, hipm
            for lep in leps:
                lepstr    = lep+" "
                if "Ele" in lep: lepstr = "Electron"+" "
                lep_syst  = dict(all_syst[lep], **all_syst["Both"])
                lep_syst["centralNLO"] = "centralNLO"
                sample    = year+lep
                samplenm  = year+hipm+lep
                samplefol = "Output/hadd/"
                outputnm  = samplefol+"ratio_"+samplenm+".root"
                sampleloc = samplefol+"merge_"+samplenm+".root"
                hsample   = TFile(sampleloc,"READ","input_file")
                foutput   = TFile(outputnm, "RECREATE", "output_file")
                
                print "input sample", sampleloc
                hSFstaterr     = TH2D(sample+"staterr", sample+"staterr, ",  nbinX, xEdges, nbinY, yEdges)
                hSFsysterr     = TH2D(sample+"systerr", sample+"systerr, ",  nbinX, xEdges, nbinY, yEdges)
                hSFerr         = TH2D(sample+"err"    , sample+"err, "    ,  nbinX, xEdges, nbinY, yEdges)
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
                hSFDataMC_cen  = heffData_cen.Clone(year+" hSFDataMCcentral")
                hSFDataMC_cen.Divide(heffMC_cen)

                for syst in lep_syst:
                    if "Muon" in lep and "NLO" in syst: continue
                    hfolder   = folbase+syst+'/'
                    os.system("mkdir -p "+hfolder)
                    #if "central" not in syst: continue 
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
                        labels    = syst+";#eta;"+lepstr+"p_{T}"
                        Mstr      = ''
                        if "M" in M: 
                            hist_type = ''
                            labels    = syst+" Mass ;"+lepstr+"p_{T}"
                            Mstr      = "_Mass"
                        heffData.Divide(hbaseData)
                        heffData.SetTitle(year+" allcuts/basecuts (Data) "+labels)
                        heffData.Draw(hist_type)
                        heffData.Write()
                        #c1.SaveAs(hfolder+"eff_"+sample+syst+Mstr+"_Data.png")
                        heffMC.Divide(hbaseMC)
                        heffMC.SetTitle(year+" allcuts/basecuts (MC) "+labels)
                        heffMC.Draw(hist_type)
                        heffMC.Write()
                        #c1.SaveAs(hfolder+"eff_"+sample+syst+Mstr+"_MC.png")

                        if syst != "central":
                            hSFDataMC  = heffData.Clone(year+" hSFDataMC"+M+syst)
                            hSFDataMC.Divide(heffMC)
                            hSFDataMC.SetTitle(year+" SF eff_{data}/eff_{MC} "+labels)
                            hSFDataMC.Draw(hist_type)
                            hSFDataMC.Write()
                            #c1.SaveAs(hfolder+"SF_"+sample+syst+Mstr+"_DataMC.png")

                        heffDataerr = heffData.Clone(year+"heffDataerr" +M+syst)
                        heffMCerr   = heffMC.Clone(  year+"heffMCerr"   +M+syst)
                        if "M" in M: continue

    
                        if "MET50" in syst: continue
                        passeschecks = False
                        #print done_muontag, done_tnpmass, "syst", syst, bool("tagMu" in syst)
                        if (done_muontag and "tagMu" in syst) or (done_tnpmass and "TnP_m" in syst):
                            passeschecks = True
                            if   "TnP_m" in syst: othersyst = othersystmass
                            elif "tagMu" in syst: othersyst = othersystMtag
                            else:
                                print "something is wrong, check it out"
                                exit()

                        #print "\nim about to calculate the plots\n"
                        #print syst, done_tnpmass, done_muontag
                        for i in range(1,hSFerr.GetNbinsX() + 1):
                            for j in range(1,hSFerr.GetNbinsY() + 1):
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
                                    #if "TnP_m" in syst and done_tnpmass is True:
                                    central_iSF = hSFDataMC_cen.GetBinContent(i,j)
                                    syst_iSF    = hSFDataMC.GetBinContent(i,j)
                                    syst_allSF  = hSFsysterr.GetBinContent(i,j)
                                    
                                    if syst_iSF>0: syst_idiff  = (central_iSF-syst_iSF)**2
                                    else         : syst_idiff  = 0
                                    
                                    #if "":
                                    if "tagMu" in syst or "TnP_m" in syst:
                                        if passeschecks:
                                            otherSF     = foutput.Get(year+" hSFDataMC"+M+othersyst)
                                            other_idiff = (central_iSF-otherSF.GetBinContent(i,j))**2
                                            syst_idiff  =  max(syst_idiff, other_idiff)
                                        else: 
                                            syst_idiff  = 0
                                    #if j==5: print "syst", i,j, np.sqrt(syst_idiff)
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
                for i in range(1,hSFerr.GetNbinsX() + 1):
                    for j in range(1,hSFerr.GetNbinsY() + 1):
                        allsysterrsq_i = hSFsysterr.GetBinContent(i,j)
                        allstaterr_i   = hSFstaterr.GetBinContent(i,j)
                        allerr_i       = np.sqrt(allsysterrsq_i+allstaterr_i**2)
                        #print i, j, allerr_i, allstaterr_i, np.sqrt(allsysterrsq_i)
                        hSFerr.SetBinContent(i,j, allerr_i)
                        hSFDataMC_cen.SetBinError(i,j, allerr_i)
                hSFstaterr.Write()
                hSFsysterr.Write()        
                hSFerr.Write()
                
                hSFDataMC_cen.GetYaxis().SetRangeUser(20,200)
                hSFDataMC_cen.SetMinimum(0.9)
                hSFDataMC_cen.SetMaximum(1.05)
                hSFDataMC_cen.SetTitle(year+" SF eff_{data}/eff_{MC} "+labels)
                hSFDataMC_cen.Draw("Ecolztext")
                hSFDataMC_cen.Write()
                
                c1.SaveAs(fcentral+"SF_"+sample+Mstr+"_DataMC_cen.png")
                
                
                hSFsysterr.SetTitle(year+" SF syst err eff_{data}/eff_{MC} "+labels)
                hSFsysterr.Draw("colztext")
                c1.SaveAs(fcentral+"SF_systerr"+sample+Mstr+"_DataMC.png")
                hSFstaterr.SetTitle(year+" SF stat err eff_{data}/eff_{MC} "+labels)
                hSFstaterr.Draw("colztext")
                c1.SaveAs(fcentral+"SF_staterr"+sample+Mstr+"_DataMC.png")
                hSFerr.SetTitle(year+" SF err eff_{data}/eff_{MC} "+labels)
                hSFerr.Draw("colztext")
                c1.SaveAs(fcentral+"SF_err"+sample+Mstr+"_DataMC.png")
                                

    print "All systematics processed, now saving it to the web..."
    www = os.getenv('WWW')
    wloc = www+'/susy/tagAndProbe'
    os.system('mkdir -p '+wloc)
    os.system('cp -r Histograms '+wloc)
    os.system('cp '+www+'/index.php '+wloc+"/Histograms/")
    for year in years:
        hipms = addHipm(year)
        for hipm in hipms:
            for lep in leps:
                lep_syst  = dict(all_syst[lep], **all_syst["Both"])
                for syst in lep_syst:
                    print year, hipm, syst
                    #continue
                    os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+year+hipm+"/")
                    os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+year+hipm+"/"+syst+"/")###
    
