import os, shutil
import SimpleITK as sitk
import cv2
import glob

BMPDIR = '/root/Share/data' # BMPDIR is path for directory which has many directories that has a bunch of bmp images.
NIIDIR = '/root/Share/nii'

class bmp2nii():
    def __init__(self, DATADIR):
        self.OCTs = []
        self.i_OCTs = []
        self.datadir = DATADIR
        self.niidir = ''
        
    
    def __call__(self, niidir):
        self.niidir = niidir
        if os.path.isdir(self.niidir): pass
        else: os.mkdir(self.niidir)
        for f in os.listdir(self.datadir):
            idx = f.split('.')[0] # OCT file has 5 legth number like 10001
            if len(idx)==5: # not rendered data.
                self.i_OCTs.append(int(idx))
        self.i_OCTs = sorted(self.i_OCTs)

        for i in self.i_OCTs:
            self.OCTs.append(os.path.join(self.datadir,str(i)))

        cnt = 0
        for OCT in self.OCTs:
            if cnt == 5: return
            datanum=OCT.split('/')[-1]
            print(f'[{datanum}] : ',end='')
            self.bmp2nii(OCT,datanum)
            print('all the bmp images are converted to nii.')
            cnt +=1
    

    def bmp2nii(self, OCT, dnum):
        '''
        making multiple bmp files to one nii.gz file
        '''
        OCT_sorted = sorted(glob.glob(os.path.join(OCT,'*.bmp')), key=os.path.getmtime) # sorting files in directory
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(OCT_sorted)
        vol = reader.Execute()
        niiname = f'{dnum}.nii.gz'
        niipath = os.path.join(self.niidir, niiname)
        sitk.WriteImage(vol, niipath)

convert = bmp2nii(BMPDIR)(NIIDIR)
