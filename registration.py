import os
import numpy as np
import nibabel as nib
import SimpleITK as sitk

def get_parameter_map(fix_path, subject, mov_before_dir, mov_after_dir, parameter_dir, isMask=False):
    mov_before_path = os.path.join(mov_before_dir, f'{subject}.nii.gz')
    mov_after_path = os.path.join(mov_after_dir, f'{subject}.nii.gz')

    map_translate_path = os.path.join(parameter_dir, f'{subject}_translate.txt')
    map_rigid_path = os.path.join(parameter_dir, f'{subject}_rigid.txt')
    map_affine_path = os.path.join(parameter_dir, f'{subject}_affine.txt')

    elastix_img_filter = sitk.ElastixImageFilter()
    elastix_img_filter.LogToConsoleOn()
    elastix_img_filter.SetFixedImage(sitk.ReadImage(fix_path, sitk.sitkUInt8))
    elastix_img_filter.SetMovingImage(sitk.ReadImage(mov_before_path, sitk.sitkUInt8))

    parmeter_vector = sitk.VectorOfParameterMap()

    set_translation_map()
    
    
    
        
        
