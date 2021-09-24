import ROOT, os, glob, sys

def confirm():
    answer = raw_input("OK to push to continue [Y/N]? ").lower()
    if "y" not in answer:
        print "exiting..."
        exit()

if __name__ == '__main__':
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


    PWD     = ''#os.getenv('PWD')+'/'
    outfol  = PWD+"old_Output/"
    folders = os.listdir(outfol)
    cmsenv  = ' eval `scramv1 runtime -sh` '
    os.system("mkdir -p "+outfol+"/hadd") 

    foladd  = []
    for folder in folders: 
        if datamc not in folder or year not in folder or lep not in folder: continue
        foladd.append(folder)
    print "folders to hadd:", foladd
    for folder in foladd:
        files   = glob.glob(outfol+folder+"/*part*.root")
        print "hadding for folder", folder#, files
        command = cmsenv+"; hadd -f "+outfol+"hadd/"+folder+".root "+" ".join(files) 
        os.system(command)
        #print command
