import cv2
import glob
import os, shutil
import SimpleITK as sitk
import nibabel   as nib

BMPDIR = '/root/Share/data' # BMPDIR is path for directory which has many directories that has a bunch of bmp images.
NIIDIR = '/root/Share/nii'

class bmp2nii():
    def __init__(self, DATADIR):
        self.OCTs = []
        self.i_OCTs = []
        self.datadir = DATADIR
        self.niidir = ''
        self.niiname = ''
        self.niipath = ''
        
    
    def __call__(self, niidir, header=False):
        self.niidir = niidir
        if os.path.isdir(self.niidir): pass
        else: os.mkdir(self.niidir)
        self.head = header

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
        self.niiname = f'{dnum}.nii.gz'
        self.niipath = os.path.join(self.niidir, self.niiname)
        sitk.WriteImage(vol, self.niipath)
        #adding header if there's header file's path
        if self.head:
            self.addHeader()

    def addHeader(self):
        '''
        add header with .mhd file
        '''
        nib_img= nib.load(self.niipath)
        print(nib_img.header)
        input()

convert = bmp2nii(BMPDIR)(NIIDIR, header=True)
