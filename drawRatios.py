from        loop import *
from submit_loop import *
from        ROOT import gROOT, gStyle

gStyle.SetOptStat(0);
gROOT.SetBatch(True)
gStyle.SetPaintTextFormat("4.3f");

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
                lep_syst  = dict(all_syst[lep], **all_syst["Both"])
                lep_syst["centralNLO"] = "centralNLO"
                sample    = year+lep
                samplenm  = year+hipm+lep
                samplefol = "b_Output/hadd/"
                outputnm  = samplefol+"ratio_"+samplenm+".root"
                sampleloc = samplefol+"merge_"+samplenm+".root"
                hsample   = TFile(sampleloc,"READ","input_file")
                foutput   = TFile(outputnm, "RECREATE", "output_file")
                
                print "input sample", sampleloc


                for syst in lep_syst:
                    if "Muon" in lep and "NLO" in syst: continue
                    hfolder   = 'Histograms/'+year+"/"+syst+'/'
                    os.system("mkdir -p "+hfolder)

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
                        labels    = syst+";#eta; p_{T}"
                        Mstr      = ''
                        if "M" in M: 
                            hist_type = ''
                            labels    = syst+" Mass ; p_{T}"
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

                     
    www = os.getenv('WWW')
    wloc = www+'/susy/tagAndProbe'
    os.system('mkdir -p '+wloc)
    os.system('cp -r Histograms '+wloc)
    os.system('cp '+www+'/index.php '+wloc+"/Histograms/")
    for year in years:
        for syst in lep_syst:
            os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+year+"/")
            os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+year+"/"+syst+"/")
    
