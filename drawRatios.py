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
    
    print "Making plots for",datamcs, years, leps, "and", NLO
    #confirm()

    for year in years:
        hipms = addHipm(year)
        for hipm in hipms:
            for lep in leps:
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

                c1 = TCanvas( 'c1', 'Ratio plot', 200,10, 1600, 900 )

                for syst in lep_syst:
                    if "Muon" in lep and "NLO" in syst: continue
                    hfolder   = 'Histograms/'+syst+'/'
                    os.system("mkdir -p "+hfolder)

                    print "systematic",syst
                    systD =syst
                    if "NLO" in syst: systD = 'central' 
                    hbaseData  =  hsample.Get("data"+sample+"base"+systD)
                    hallData   =  hsample.Get("data"+sample+"all" +systD)
                    hbaseMC    =  hsample.Get(  "mc"+sample+"base"+syst)
                    hallMC     =  hsample.Get(  "mc"+sample+"all" +syst)
                    hbaseratio =  hbaseData.Clone("hbaseratio" +syst)
                    hallratio =  hbaseData.Clone("hallratio" +syst)
                    hbaseratio.Divide(hbaseMC)
                    hbaseratio.Draw("colz text")
                    hbaseratio.Write()
                    c1.SaveAs(hfolder+"ratio_"+sample+syst+"_base.png")
                    hallratio.Divide(hbaseMC)
                    hallratio.Draw("colz text")
                    hallratio.Write()
                    c1.SaveAs(hfolder+"ratio_"+sample+syst+"_all.png")

    www = os.getenv('WWW')
    wloc = www+'/susy/tagAndProbe'
    os.system('mkdir -p '+wloc)
    os.system('cp -r Histograms '+wloc)
    os.system('cp '+www+'/index.php '+wloc+"/Histograms/")
    for syst in lep_syst:
        os.system('cp '+www+'/index.php '+wloc+"/Histograms/"+syst+"/")
    
