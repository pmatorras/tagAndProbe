from        loop import *
from submit_loop import *
from        ROOT import gROOT, gStyle

gStyle.SetOptStat(0);
gROOT.SetBatch(True)
gStyle.SetPaintTextFormat("4.3f");

print xEdges, yEdges


def getEff_i(heff, hbase, i,j, isMC=False):
    val_i = heff.GetBinContent(i,j)
    multi = 1
    if isMC: multi=1000
    if heff.GetBinContent(i,j) >0:
        err_i = np.sqrt(heff.GetBinContent(i,j)*(1-heff.GetBinContent(i,j))/(multi*hbase.GetBinContent(i,j)))
    else: 
        err_i = 0
    print "binning thingy", heff.GetBinContent(i,j),hbase.GetBinContent(i,j)
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
                hSFstaterr = TH2D(sample+"staterr", sample+"staterr, ",  nbinX, xEdges, nbinY, yEdges)
                hSFsysterr = TH2D(sample+"systerr", sample+"systerr, ",  nbinX, xEdges, nbinY, yEdges)
                hSFerr     = TH2D(sample+"err"    , sample+"err, "    ,  nbinX, xEdges, nbinY, yEdges)

                for syst in lep_syst:
                    if "Muon" in lep and "NLO" in syst: continue
                    folbase   = 'Histograms/'+year+'/'
                    hfolder   = folbase+syst+'/'
                    os.system("mkdir -p "+hfolder)
                    #if "central" not in syst: continue 
                    print "SYSTEMATIC",syst
                    systD =syst
                    if "NLO" in syst: systD = 'central' 
                    for M in ["","M"]:
                        hbaseData  =  hsample.Get("data"+sample+"base"+M+systD)
                        hallData   =  hsample.Get("data"+sample+"all" +M+systD)
                        hbaseMC    =  hsample.Get(  "mc"+sample+"base"+M+syst)
                        hallMC     =  hsample.Get(  "mc"+sample+"all" +M+syst)
                        
                        print  "getting", hallData, "data"+sample+"base"+M+systD
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
                        c1.SaveAs(hfolder+"eff_"+sample+syst+Mstr+"_Data.png")
                        heffMC.Divide(hbaseMC)
                        heffMC.SetTitle(year+" allcuts/basecuts (MC) "+labels)
                        heffMC.Draw(hist_type)
                        heffMC.Write()
                        c1.SaveAs(hfolder+"eff_"+sample+syst+Mstr+"_MC.png")


                        hSFDataMC  = heffData.Clone(year+" hSFDataMC"+M+syst)
                        hSFDataMC.Divide(heffMC)
                        hSFDataMC.SetTitle(year+" SF eff_{data}/eff_{mc} "+labels)
                        hSFDataMC.Draw(hist_type)
                        hSFDataMC.Write()
                        c1.SaveAs(hfolder+"SF_"+sample+syst+Mstr+"_DataMC.png")

                        heffDataerr = heffData.Clone(year+"heffDataerr" +M+syst)
                        heffMCerr   = heffMC.Clone(  year+"heffMCerr"   +M+syst)
                        if "M" in M: continue
                        if "central" not in syst:
                            hbaseData_cen  =  hsample.Get("data"+sample+"base"+M+"central")
                            hallData_cen   =  hsample.Get("data"+sample+"all" +M+"central")
                            hbaseMC_cen    =  hsample.Get(  "mc"+sample+"base"+M+"central")
                            hallMC_cen     =  hsample.Get(  "mc"+sample+"all" +M+"central")
                            heffData_cen   =  hallData_cen.Clone("heffData" +M+"central")
                            heffMC_cen     =  hallMC_cen.Clone("heffMC" +M+"central")
                            
                            heffData_cen.Divide(hbaseData_cen)
                            heffMC_cen.Divide(hbaseMC_cen)
                            hSFDataMC_cen  = heffData_cen.Clone(year+" hSFDataMC"+M+syst)
                            hSFDataMC_cen.Divide(heffMC_cen)

                        for i in range(1,hSFerr.GetNbinsX() + 1):
                            for j in range(1,hSFerr.GetNbinsY() + 1):
                                allerr_iSF  = hSFerr.GetBinContent(i,j)
                                if "central" in syst:
                                    val_iMC  , err_iMC   = getEff_i(heffMC,hbaseMC, i,j, True)
                                    val_iData, err_iData = getEff_i(heffData,hbaseData,i,j)
                                    #print val_iMC, val_iData
                                    if val_iMC <1e-9 and val_iData <1e-9: err_SF = 0
                                    else:
                                        if val_iMC   < 1e-9: val_iMC   = 1e9
                                        if val_iData < 1e-9: val_iData = 1e9
                                        err_SF = np.sqrt((err_iMC/val_iMC)**2+(err_iData/val_iData)**2)
                                    allstat_iSF = hSFstaterr.GetBinContent(i,j)
                                    hSFstaterr.SetBinContent(i,j, allstat_iSF+err_SF)
                                    #hSFerr.SetBinContent(i,j, allerr_iSF+err_SF)
                                    print i, j, err_iMC, err_iData, err_SF
                                else:
                                    central_iSF = hSFDataMC_cen.GetBinContent(i,j)
                                    syst_iSF    = hSFDataMC.GetBinContent(i,j)
                                    syst_allSF  = hSFsysterr.GetBinContent(i,j)
                                    if syst_iSF>0: sist_idiff  = (central_iSF-syst_iSF)**2
                                    else         : sist_idiff  = 0
                                    hSFsysterr.SetBinContent(i,j,syst_allSF+sist_idiff)
                                    if j==5: print syst, i, j, np.sqrt(sist_idiff), central_iSF, syst_iSF
                #do the rest
                for i in range(1,hSFerr.GetNbinsX() + 1):
                    for j in range(1,hSFerr.GetNbinsY() + 1):
                        allsysterrsq_i = hSFsysterr.GetBinContent(i,j)
                        allstaterr_i   = hSFstaterr.GetBinContent(i,j)
                        allerr_i       = np.sqrt(allsysterrsq_i+allstaterr_i**2)
                        print "values",i, j, allerr_i, allstaterr_i, np.sqrt(allsysterrsq_i)
                        hSFerr.SetBinContent(i,j, allerr_i)
                hSFstaterr.Write()
                hSFsysterr.Write()        
                hSFerr.Write()
                
                fcentral = folbase+"central/"
                hSFsysterr.SetTitle(year+" SF syst err eff_{data}/eff_{mc} "+labels)
                hSFsysterr.Draw("colztext")
                c1.SaveAs(fcentral+"SF_systerr"+sample+syst+Mstr+"_DataMC.png")
                hSFstaterr.SetTitle(year+" SF syst err eff_{data}/eff_{mc} "+labels)
                hSFstaterr.Draw("colztext")
                c1.SaveAs(fcentral+"SF_staterr"+sample+syst+Mstr+"_DataMC.png")
                hSFerr.SetTitle(year+" SF err eff_{data}/eff_{mc} "+labels)
                hSFerr.Draw("colztext")
                c1.SaveAs(fcentral+"SF_systerr"+sample+syst+Mstr+"_DataMC.png")
                                


    www = os.getenv('WWW')
    wloc = www+'/susy/tagAndProbe'
    os.system('mkdir -p '+wloc)
    os.system('cp -r Histograms '+wloc)
    os.system('cp '+www+'/index.php '+wloc+"/Histograms/")
    for year in years:
        for syst in lep_syst:
            os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+year+"/")
            os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+year+"/"+syst+"/")
    
