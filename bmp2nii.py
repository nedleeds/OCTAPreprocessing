import os
import glob
import numpy     as np
import nibabel   as nib
import SimpleITK as sitk
from skimage.color import rgb2gray

class bmp2nifti():
    def __init__(self):
        self.bmp_dir = ''
        self.nii_dir = ''
        self.physical_resolution = {}
        self.nii_size = {}

    def set_dir(self, load_dir, save_dir):
        self.bmp_dir = load_dir
        self.nii_dir = save_dir

    def start_convert(self):
        # check save directory first.
        os.makedirs(self.nii_dir, exist_ok=True)

        # get subject list in bmp directory.
        subject_list = sorted(os.listdir(self.bmp_dir))
        
        for subject in subject_list:
            subject_bmp_dir = os.path.join(self.bmp_dir, subject)
            self.bmp2nii(idx=subject, load_dir=subject_bmp_dir, save_dir=self.nii_dir)
            
        
    def bmp2nii(self, idx, load_dir, save_dir):
        bmp_sorted = sorted(glob.glob(os.path.join(load_dir,'*.bmp')), key=lambda x: int(x.split('/')[-1].split('.')[0]))
        # bmp to nifti by SimpleITK
        reader = sitk.ImageSeriesReader()
        reader.SetFileNames(bmp_sorted)
        nifti_image = reader.Execute()

        # change Nifti value
        nifti = sitk.GetArrayFromImage(nifti_image)
        nifti = np.sum(nifti, axis=-1)/3 # RGB -> GRAY
        nifti = nifti.transpose(2,1,0)
        
        # sitk image from array
        nifti_img = sitk.GetImageFromArray(nifti)
        nifti_img = sitk.Cast(sitk.RescaleIntensity(nifti_img), sitk.sitkUInt8)

        save_path = os.path.join(save_dir, f'{idx}.nii.gz')
        sitk.WriteImage(nifti_img, save_path)
        print(f"{idx} has been converted.")

class modify_nifti_header():
    def __init__(self) -> None:
        self.nii_size = {}
        self.physical_resolution = {}

    def set_nifti_resolution(self, nii_size, physical_resolution):
        height_nii, width_nii, depth_nii = nii_size
        height_res, width_res, depth_res = physical_resolution
        self.nii_size = {'height' : height_nii, 'width' : width_nii, 'depth' : depth_nii}
        self.physical_resolution = {'height' : height_res, 'width' : width_res, 'depth' : depth_res}
    
    def check_volume_info(self):
        nii_size = self.nii_size
        fov_size = self.fov_size
        self.physical_resolution = { k:nii_size[k]*fov_size[k] for k in ['height', 'width', 'depth'] }
        
        for k in self.physical_resolution:
            print(f'{k:6} of physical resolution :{self.physical_resolution[k]} mm')


def main():
    # This part is about converting bmp files to nifti.
    bmp_dir = '/data/IEEE-OCT500/FOV_3MM/OCT'
    nii_dir = '/data/Nifti/In/FOV_33/OCT'
    converter = bmp2nifti()
    converter.set_dir(load_dir = bmp_dir, save_dir = nii_dir)
    converter.start_convert()

    # This part is about modifying header info for 
    # proper 3D render view based on FOV.
    scale = 32
    fov33_size = (3*scale, 2*scale, 3*scale) 
    nii33_size = (304, 640, 304)
    # fov66_size = (6, 6, 2)
    # nii66_size = (400, 640, 400)
    modifier = modify_nifti_header()
    modifier.set_nifti_resolution(nii_size = nii33_size,
                                  physical_resolution = fov33_size)
    modifier.check_volume_info()
    

main()