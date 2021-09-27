import ROOT, os, glob, sys
from submit_loop import * 
def confirm():
    answer = raw_input("OK to push to continue [Y/N]? ").lower()
    if "y" not in answer:
        print "exiting..."
        exit()

if __name__ == '__main__':
    '''
    datamc = ''
    year   = ''
    lep    = '' 
    if len(sys.argv)<4:
        print 'You didnt specify datamcs, year and lep, in that order'
        confirm()
        if len(sys.argv)>1: datamc = sys.argv[1]  
        if len(sys.argv)>2: year   = sys.argv[2]
    else:
        datamc = sys.argv[1]
        year   = sys.argv[2]
        lep    = sys.argv[3]

    if   "e" in lep.lower(): lep = "Ele"
    elif "m" in lep.lower(): lep = "Muon"

    '''
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
            for lep in leps:
                if "merge" in datamc:
                    fol_hadd = outfol+"hadd/"
                    all_hadd = os.listdir(fol_hadd)
                    sel_hadd = []
                    for haddf in all_hadd:
                        if year not in haddf or lep not in haddf: continue
                        sel_hadd.append(fol_hadd+haddf+" ")
                    print "selected files", sel_hadd
                    if len(sel_hadd)!=2:
                        print "should be two files, exiting..."
                        exit()
                    else:
                        command = cmsenv+"; hadd -f "+fol_hadd+"merge_"+year+lep+".root "+sel_hadd[0]+sel_hadd[1]
                        print command
                else:
                    foladd  = []
                    for folder in folders: 
                        if datamc not in folder or year not in folder or lep not in folder: continue
                        foladd.append(folder)
                    print "folders to hadd:", foladd
                    #exit()
                    for folder in foladd:
                        files   = glob.glob(outfol+folder+"/*part*.root")
                        print "hadding for folder", folder#, files
                        command = cmsenv+"; hadd -f "+outfol+"hadd/"+folder+".root "+" ".join(files) 
                        os.system(command)
                        #print command
