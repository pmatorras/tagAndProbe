{
  
  Bool_t isMuon = true;
  char *filenm = "";
  char *histname = "";
  if (isMuon == true){
    filenm  = "../LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017v8/Efficiencies_muon_generalTracks_Z_Run2017_UL_ID.root";
    histname = "NUM_SoftID_DEN_TrackerMuons_abseta_pt_efficiencyData_stat";

  } else{
    filenm = "../LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017/ElectronScaleFactors_Run2017_SUSY.root";
    histname= "Run2017_CutBasedVetoNoIso94XV1";

  }
  cout<<"filenm:\t"<<filenm<< "hist:\t"<<histname<<endl;

  TFile* hfile = new TFile(filenm,"READ");    
  TH2D*   hist = (TH2D*) hfile->Get(histname); 
  Int_t  nBinX = hist->GetNbinsX();
  Int_t  nBinY = hist->GetNbinsY();
  cout << "nbinns" << nBinX<< " "<< nBinY<<endl;
 
  for (Int_t ibx = 1; ibx <= nBinX; ibx++) {
    for (Int_t iby = 1; iby <= nBinY; iby++) {
      Double_t  xBinMin = hist->GetXaxis()->GetBinLowEdge(ibx);
      Double_t  xBinMax = hist->GetXaxis()->GetBinUpEdge(ibx);
      Double_t  yBinMin = hist->GetYaxis()->GetBinLowEdge(iby);
      Double_t  yBinMax = hist->GetYaxis()->GetBinUpEdge(iby);
      Double_t nBinCont = hist->GetBinContent(ibx,iby);

      cout << " bin " << ibx << " " << iby ;
      cout << " xBin: " << xBinMin << " - " << xBinMax;
      cout << ", yBin: " << yBinMin << " - " << yBinMax;
      cout << ", content: " << nBinCont << endl;
    }
  }

}
