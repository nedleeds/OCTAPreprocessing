import cv2
import glob
import os, shutil
import SimpleITK as sitk
import nibabel   as nib
import numpy     as np
from skimage.color import rgb2gray

BMPDIR = '/root/Share/data/OCTA-500_6M_OCT' # BMPDIR is path for directory which has many directories that has a bunch of bmp images.
NIIDIR = '/root/Share/data/nii'

class bmp2nii():
    def __init__(self, DATADIR):
        self.OCTs = []
        self.i_OCTs = []
        self.datadir = DATADIR
        self.niidir = ''
        self.niiname = ''
        self.niipath = ''
        self.vol = 0
        
    def __call__(self, niidir, header_=False):
        self.niidir = niidir
        if os.path.isdir(self.niidir): pass
        else: os.mkdir(self.niidir)
        self.head_ = header_

        for f in os.listdir(self.datadir):
            idx = f.split('.')[0]           # OCT file has 5 legth number like 10001
            if len(idx)==5:                 # not rendered data.
                self.i_OCTs.append(int(idx))

        self.i_OCTs = sorted(self.i_OCTs)
        for i in self.i_OCTs:
            self.OCTs.append(os.path.join(self.datadir,str(i)))

        cnt = 0
        for OCT in self.OCTs:
            # if cnt == 1: return
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
        self.vol = reader.Execute()

        image_array = sitk.GetArrayFromImage(self.vol)    #z, y, x
        grayscale = rgb2gray(image_array)
        g_image = sitk.GetImageFromArray(grayscale)
        
        # self.convertAxis() 
        self.niiname = f'{dnum}.nii.gz'
        self.niipath = os.path.join(self.niidir, self.niiname)
        sitk.WriteImage(g_image, self.niipath)
        
        # adding header if there's header file's path
        if self.head_ : self.addHeader(dnum)
        
        # nib_img= nib.load(self.nibpath)
        # print(nib_img.header)


    def convertAxis(self):
        # do I really need to convert axis? No I don't. rendering is working for world coordinate, and it's RAS.
        # -> As data was collected with this coordinate, I don't need to convert the axes for rendering.
        v = sitk.GetArrayFromImage(self.vol) # S/I:400(x), A/P:640(y), R/L: 400(z) normal coordinate (matched with real eye position)
        v = np.swapaxes(v,1,0)               # S/I:640(y), A/P:400(x), R/L: 400(z)
        v = np.swapaxes(v,1,2)               # S/I:640(y), A/P:400(z), R/L: 400(x)
        v = np.flipud(v)                     # S/I:640(y), A/P:400(z), R/L: 400(x) --> flip up and down
        
        print(f'after convert: S/I:{v.shape[0]}, A/P:{v.shape[1]}, R/L:{v.shape[2]}')
        self.vol = sitk.GetImageFromArray(v)

    def addHeader(self,dnum):
        '''
        add header
        '''
        nib_img= nib.load(self.niipath)
        # print(swi.header)
        head = nib_img.header
        head['dim'][0:4]=[3,400,640,400]
        head['pixdim'][1:4]=[15,3.125,15]
        head['xyzt_units']='3'
        head['qform_code']='0'

        c = np.array(nib_img.get_fdata())
        nib_img2 = nib.Nifti1Image(c, nib_img.affine, header=head)
        head2 = nib_img2.header
        head2['dim'][0:4]=[3,400,640,400] #<---------------Not working ...
        head2['pixdim'][1:4]=[15,3.125,15]
        head2['xyzt_units']='3'

        self.nibname = dnum+'.nii.gz'
        self.nibpath = os.path.join(NIIDIR, self.nibname)

        nib.save(nib_img2, self.nibpath)
        

        
        
convert = bmp2nii(BMPDIR)(NIIDIR, header_=True)
