import ROOT, os, glob, sys
from submit_loop import * 
def confirm():
    answer = raw_input("OK to push to continue [Y/N]? ").lower()
    if "y" not in answer:
        print "exiting..."
        exit()

if __name__ == '__main__':

    PWD     = ''#os.getenv('PWD')+'/'
    outfol  = PWD+"Output/"
    print "getting input from "+ outfol

    folders = os.listdir(outfol)
    cmsenv  = ' eval `scramv1 runtime -sh` '
    os.system("mkdir -p "+outfol+"/hadd") 

    datamcs, years, leps, NLO = getinputs()

    print "hadding for",datamcs, years, leps, "and", NLO
    confirm()
    for datamc in datamcs:
        for year in years:
            if "16" in year: hipms = ['_HIPM', '_noHIPM']
            else           : hipms = ['']
            for hipm in hipms:
                for lep in leps:
                    if "merge" in datamc:
                        fol_hadd = outfol+"hadd/"
                        all_hadd = os.listdir(fol_hadd)
                        sel_hadd = []
                        for haddf in all_hadd:
                            if year not in haddf or lep not in haddf or hipm not in haddf: continue
                            sel_hadd.append(fol_hadd+haddf+" ")
                        print "selected files", sel_hadd
                        if len(sel_hadd)<2:
                            print "should be at least two files, exiting..."
                            exit()
                        else:
                            command = cmsenv+"; hadd -f "+fol_hadd+"merge_"+year+hipm+lep+".root "+sel_hadd[0]+sel_hadd[1]
                            if len(sel_hadd) == 3: 
                                command+=sel_hadd[2]
                            else: 
                                print "too many files, exiting..."
                                exit()
                            print command
                            os.system(command)
                    else:
                        foladd  = []
                        for folder in folders: 
                            if datamc not in folder or year not in folder or lep not in folder or hipm not in folder: continue
                            foladd.append(folder)
                        print "folders to hadd:", foladd
                        #exit()
                        for folder in foladd:
                            files   = glob.glob(outfol+folder+"/*part*.root")
                            print "hadding for folder", folder#, files
                            command = cmsenv+"; hadd -f "+outfol+"hadd/"+folder+".root "+" ".join(files) 
                            os.system(command)
                            #print command
