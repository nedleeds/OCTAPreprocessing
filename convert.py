import os
import glob
import numpy     as np
import nibabel   as nib
import SimpleITK as sitk
from skimage.color import rgb2gray


BMPDIR_OCT   = './data/OCTA-500_6M_OCT' # BMPDIR is path for directory which has many directories that has a bunch of bmp images.
BMPDIR_OCTA  = './data/OCTA-500_6M_OCTA' # BMPDIR is path for directory which has many directories that has a bunch of bmp images.
NIIDIR_OCT   = './data/Nifti/In/FOV_66/OCT'
NIIDIR_OCTA  = './data/Nifti/In/FOV_66/OCTA'
NIIDIR_BEFORE= './data/Nifti/In/FOV_66/HeaderTest/Before' 
NIIDIR_AFTER = './data/Nifti/In/FOV_66/HeaderTest/After/OCT' 
NIIDIR_CVLT  = './data/Nifti/In/FOV_66/Curvelet_SRL' 
NII_HEADER_PATH  = './data/Nifti/In/FOV_66/OCT/Segmented/10001_oct/10001_oct_OCT_Iowa.nii.gz'

class bmp2nifti():
    def __init__(self, BMPDIR):
        self.OCTs    = []
        self.bmpdir = BMPDIR
        self.niidir  = ''
        self.niiname = ''
        self.niipath = ''
        self.vol     = 0
        
    def __call__(self, NIIDIR):
        self.checkNiiDir(NIIDIR)

        dir_nums = list(self.getDirNums())
        
        for idx in dir_nums:
            bmp_path = os.path.join(self.bmpdir, str(idx))
            nii_path = os.path.join(self.niidir, str(idx))
            if idx>10199: self.bmp2nii(bmp_path, nii_path)
            else: pass
            print(f"{idx} has been converted.")

    def checkNiiDir(self, niidir):
        if os.path.isdir(niidir): pass
        else: os.mkdir(niidir)
        self.niidir = niidir
    
    def getDirNums(self):
        dirNums = []
        for f in os.listdir(self.bmpdir):
            idx = f.split('.')[0]           # OCT file has 5 legth number like 10001
            if len(idx)==5:                 # not rendered data.
                dirNums.append(int(idx))
        dirNums = sorted(dirNums)
        yield from dirNums
        
    def bmp2nii(self, bmp_path, NII_PATH):
        bmp_sorted = sorted(glob.glob(os.path.join(bmp_path,'*.bmp')), key=lambda x: int(x.split('/')[-1].split('.')[0]))
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(bmp_sorted)
        nifti = reader.Execute()
        nifti = sitk.GetArrayFromImage(nifti)
        nifti = np.sum(nifti, axis=-1)/3 # RGB -> GRAY
        nifti = next(self.convertAxis(nifti))

        NII_PATH = NII_PATH + ".nii"
        self.addHeader(NII_HEADER_PATH, NII_PATH, nifti)

    def addHeader(self, nii_header_path, nii_dst_dir, nifti):
        nifti_header = nib.load(nii_header_path)
        header = nifti_header.header  # get IOWA Header file
        header['data_type'] = b'uint8'
        header['db_name'] = b'IEEE-OCTA500'
        header['dim_info']=b'3'
        header['dim'][0:4]=[3,400,640,400]
        header['pixdim'][0:4]=[1.,15.,3.125,15.]
        header['datatype'] = b'2'
        header['slice_start'] = b'0'
        header['slice_end'] = b'639'
        header['slice_code'] = b'2'
        header['xyzt_units'] = b'3'
        header['cal_max'] = float(f"{np.max(nifti)}")
        header['cal_min'] = float(f"{np.min(nifti)}")
        header['descrip'] = "Convert from .bmp to Nifti by DHL(email:llee.dh@gmail.com)"
        new_affine = np.asarray([[-15.0,0.,0.,0.], 
                                 [0.,-3.125,0.,0.], 
                                 [0.,0.,15.,0.], 
                                 [0.,0.,0.,1.]])

        nifti_new = nib.Nifti1Image(nifti, affine=new_affine, header=header)  
        nifti_num = nii_dst_dir.split('.')[1].split('/')[-1]
        nii_dir_dst = os.path.join(nii_dst_dir, f"{nifti_num}.nii")
        nib.save(nifti_new, nii_dst_dir) # saving with as same as nifti name that I've just made.

        #check
        v = nib.load(nii_dst_dir)
        print(v.header['cal_max'], v.header['cal_min'])

    def convertAxis(self, v):
        v=v.transpose(2,1,0)
        yield v

convert = bmp2nifti(BMPDIR_OCT)(NIIDIR_AFTER)      
# convert = bmp2nifti(BMPDIR_OCTA)(NIIDIR_AFTER)


class modifyHeader():
    def __init__(self,nii_dir_src):
        self.nii_dir_src = nii_dir_src
        
    def __call__(self, nii_dir_dst):
        self.nii_dir_dst = nii_dir_dst
        nii_sorted = sorted(glob.glob(os.path.join(self.nii_dir_src,'*.nii.gz')), key=lambda x: int(x.split('/')[-1].split('.')[0].split('_')[0]))
        for c in nii_sorted:
            self.modifiyHeader(str(c))
            print(c.split('/')[-1].split('.')[0], "has been updated")

    
    def modifiyHeader(self, niipath):
        nifti = nib.load(niipath)  # load nii which just has been made in ~/Nifti/In/OCT/10001.nii.gz
        nifti_img = next(self.normalizing(nifti.get_fdata()))
        nifti_header = nifti.header
        nifti_header['data_type'] = b'uint8'
        nifti_header['db_name'] = b'IEEE-OCTA500'
        nifti_header['dim_info']="3"
        nifti_header['dim'][0:4]=[3,400,640,400]
        nifti_header['pixdim'][0:4]=[1.,15.,3.125,15.]
        nifti_header['datatype'] = "2"
        nifti_header['xyzt_units'] = "3"
        nifti_header['cal_max'] = float(f"{np.max(nifti_img)}")
        nifti_header['cal_min'] = float(f"{np.min(nifti_img)}")
        nifti_header['descrip'] = "Convert from .bmp to Nifti by DHL(email:llee.dh@gmail.com)"
        
        nifti_new = nib.Nifti1Image(nifti_img, nifti.affine, header=nifti_header)  
        nifti_num = niipath.split('.')[0].split('/')[-1]
        nii_dir_dst = os.path.join(self.nii_dir_dst, f"{nifti_num}.nii")
        nib.save(nifti_new, nii_dir_dst) # saving with as same as nifti name that I've just made.

    def normalizing(self, volume):
        M = np.max(volume)
        m = np.min(volume)
        volume = ((volume-m)/(M-m))

        yield volume
# modify_header = modifyHeader(NIIDIR_BEFORE)(NIIDIR_AFTER)
