{
  Int_t   nBinX = 5;
  Int_t   nBinY = 5;
  Double_t xMin = 0.;
  Double_t xMax = 1.;
  Double_t yMin = 0.;
  Double_t yMax = 1.;
  char  *filenm = "../LatinoAnalysis/NanoGardener/python/data/scale_factor/Full2017/ElectronScaleFactors_Run2017_SUSY.root";

  cout<<"filenm:\t"<<filenm<<endl;
  TFile* hfile = new TFile(filenm,"READ");
  TH2D*   hist = (TH2D*) hfile->Get("Run2017_CutBasedVetoNoIso94XV1"); 
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
