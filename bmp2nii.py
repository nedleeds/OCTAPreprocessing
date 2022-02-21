import os
import glob
import re
import numpy     as np
import nibabel   as nib
import SimpleITK as sitk
from skimage.color import rgb2gray

class bmp2nifti():
    def __init__(self, header_information):
        self.bmp_dir = ''
        self.nii_dir = ''
        self.nii_size = []
        self.info = header_information

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
            # break
            
        
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

        self.modify_header(load_path=save_path)
        print(f"{idx} has been converted.")

    def modify_header(self, load_path):
        nifti_img = nib.load(load_path)
        nifti_data = nifti_img.dataobj
        nifti_info = nifti_img.header

        # w_resolution, h_resolution, d_resolution = self.info['resolution']
        w_spacing, h_spacing, d_spacing = self.info['spacing']
        w_origin, h_origin, d_origin = self.info['origin']

        nifti_info_new =nifti_info
        nifti_info_new['xyzt_units'] = 0
        nifti_info_new['pixdim'] = [1., w_spacing, h_spacing, d_spacing, 1., 1., 1., 1.]
        nifti_info_new['qoffset_x'] = -w_origin
        nifti_info_new['qoffset_y'] = - h_origin
        nifti_info_new['qoffset_z'] = d_origin
        nifti_info_new['srow_x'] = [-w_spacing, 0, 0, -w_origin]
        nifti_info_new['srow_y'] = [0, -h_spacing, 0, -h_origin]
        nifti_info_new['srow_z'] = [0, 0,  d_spacing,  d_origin]

        nifti_new_img = nib.Nifti1Image(nifti_data, nifti_info_new.get_best_affine())
        nib.save(nifti_new_img, load_path)

def main():
    scale = 19*3
    fov33_size = (3, 2, 3)  # fov66_size = (6, 6, 2)
    nii33_size = (304, 640, 304)    # nii66_size = (400, 640, 400)
    resolution = [(f*scale) for f in fov33_size]
    spacing = [(r/v) for r,v in zip(resolution, nii33_size)]
    origin = [-r//2 for r in resolution]
    header_info = {'origin':origin, 'resolution':resolution, 'spacing':spacing}

    # This part is about converting bmp files to nifti.
    bmp_dir = ['/data/IEEE-OCT500/FOV_3MM/OCT', '/data/IEEE-OCT500/FOV_3MM/OCTA']
    nii_dir = ['/data/Nifti/In/FOV_33/OCT','/data/Nifti/In/FOV_33/OCTA']
    converter = bmp2nifti(header_information=header_info)
    for b_dir, n_dir in zip(bmp_dir, nii_dir):
        converter.set_dir(load_dir=b_dir, save_dir=n_dir)
        converter.start_convert()


main()