import os
import numpy as np
import nibabel as nib
import SimpleITK as sitk

def get_translation_map():
    return sitk.GetDefaultParameterMap('translation')

def get_rigid_map(is_mask=False):
    map_rigid = sitk.GetDefaultParameterMap('rigid')
    map_rigid['NumberOfResolutions']=['3']
    map_rigid['FixedImagePyramid'] =['FixedShrinkingImagePyramid']
    map_rigid['MovingImagePyramid']=['MovingShrinkingImagePyramid']
    map_rigid['FixedImagePyramidSchedule'] = ['16, 4, 1']
    map_rigid['MovingImagePyramidSchedule'] = ['16, 4, 1']
    # pMap_rigid['Interpolator']=['kNearestNeighbor'] # BSplineInterpolator
    map_rigid['ResampleInterpolator']=['FinalBSplineInterpolator']
    if is_mask:
        map_rigid['FinalBSplineInterpolationOrder']=['0']
    
    return map_rigid

def get_affine_map(isMask=False):
    map_affine = sitk.GetDefaultParameterMap('affine')
    # map_affine['FixedImageDimension'] = ['3']
    # map_affine['MovingImageDimension'] = ['3']

    # # Components
    map_affine['Registration'] = ['MultiResolutionRegistration']
    map_affine['FixedImagePyramid']=['FixedRecursiveImagePyramid'] # mine:FixedShrinkingImagePyramid
    map_affine['MovingImagePyramid']=['MovingRecursiveImagePyramid']
    # map_affine['Interpolator']=['sitkNearestNeighbor'] # BSplineInterpolator
    map_affine['ResampleInterpolator']=['FinalBSplineInterpolator']
    map_affine['Resampler']=['DefaultResampler']

    map_affine['Optimizer']=['AdaptiveStochasticGradientDescent']
    map_affine['Metric']=['AdvancedNormalizedCorrelation'] #AdvancedMattesMutualInformation
    # pyramid
    map_affine['NumberOfResolutions']=['3']

    # transform
    map_affine['AutomaticTransformInitialization'] = ['true']
    map_affine['AutomaticTransformInitializationMethod'] = ['GeometricalCenter']
    map_affine['AutomaticScalesEstimation']=['true']
    map_affine['HowToCombineTransforms'] = ['Compose']

    # Optimizer
    map_affine['MaximumNumberOfIterations'] = ['2000']

    # Metric
    map_affine['NumberOfHistogramBins'] = ['32']
    map_affine['FixedLimitRangeRatio'] = ['0.0']
    map_affine['MovingLimitRangeRatio'] = ['0.0']
    map_affine['FixedKernelBSplineOrder'] = ['1']
    map_affine['MovingKernelBSplineOrder'] = ['3']

    # Several
    map_affine['ShowExactMetricValue'] = ['false']
    map_affine['ErodMask'] = ['false']
    map_affine['ErodeFixedMask']=['false']
    map_affine['ErodeMovingMask']=['false']
    map_affine['UseDifferentiableOverlap']=['false']

    # Sampler
    map_affine['ImageSampler']=['Random'] # RandomCoordinate
    # map_affine['NumberOfSpatialSamples']=['2048']
    map_affine['NewSamplesEveryIteration']=['true']
    map_affine['BSplineInterpolationOrder']=['1']
    map_affine['FinalBSplineInterpolationOrder']=['3']
    # map_affine['SamplingPercentage']=['0.5']
    # map_affine['MetricSamplingPercentage']=['0.5']
    if isMask:
        map_affine['FinalBSplineInterpolationOrder']=['0']
        # map_affine['UseBinaryFormatForTransformationParameters'] = ['true']

    ## map_affine['MovingImagePyramid']=['MovingShrinkingImagePyramid']
    # map_affine['FixedImagePyramidSchedule'] = ['24 8 24',  '18 6 18',  '12 4 12',  '6 2 6']
    # map_affine['MovingImagePyramidSchedule'] = ['24 8 24',  '18 6 18',  '12 4 12',  '6 2 6']

def get_bspline_map(is_mask):
    map_bspline = sitk.GetDefaultParameterMap('bspline')
    map_bspline['FixedImageDimension']=['3']
    map_bspline['MovingImageDimension']=['3']
    map_bspline['UseDirectionCosines']=['true']

    map_bspline['Registration']=['MultiResolutionRegistration']
    map_bspline['Interpolator']=['BSplineInterpolator']
    map_bspline['ResampleInterpolator']=['FinalBSplineInterpolator']
    map_bspline['Optimizer']=['AdaptiveStochasticGradientDescent']
    map_bspline['Metric']=['AdvancedNormalizedCorrelation'] #AdvancedMattesMutualInformation
    
    map_bspline['HowToCombineTransforms'] = ['Compose']
    map_bspline['ErodMask']=['false']

    map_bspline['NewSamplesEveryIteration'] = ['true']
    map_bspline['UseRandomSampleRegion'] = ['true']

    map_bspline['FixedImagePyramidSchedule'] = ['24 8 24', '18 6 18', '12 4 12', '6 2 6']
    map_bspline['MovingImagePyramidSchedule'] = ['24 8 24', '18 6 18', '12 4 12', '6 2 6']
    if is_mask:
        map_bspline['FinalBSplineInterpolationOrder']=['0']

def get_parameter_map(fix_path, subject, move_before_dir, move_after_dir, parameter_dir, is_mask=False):
    ''' 1) check save directory & set the path'''
    os.makedirs(move_after_dir, exist_ok=True)
    os.makedirs(parameter_dir, exist_ok=True)

    kind = 'mask' if 'VolMask' in move_before_dir else 'octa' if 'OCTA' in move_before_dir else 'oct'
    mov_before_path = os.path.join(move_before_dir, f'{subject}.nii.gz')
    mov_after_path = os.path.join(move_after_dir, f'{subject}_{kind}_translate_rigid.nii.gz')

    map_translate_path = os.path.join(parameter_dir, f'{subject}_translate.txt')
    map_rigid_path = os.path.join(parameter_dir, f'{subject}_rigid.txt')
    # map_affine_path = os.path.join(parameter_dir, f'{subject}_affine.txt')
    # map_bspline_path = os.path.join(parameter_dir, f'{subject}_bspline.txt')

    ''' 2) init Elastix filter and set the fix and moving image ''' 
    elastix_img_filter = sitk.ElastixImageFilter()
    elastix_img_filter.LogToConsoleOff()
    elastix_img_filter.SetFixedImage(sitk.ReadImage(fix_path, sitk.sitkUInt8))
    elastix_img_filter.SetMovingImage(sitk.ReadImage(mov_before_path, sitk.sitkUInt8))

    ''' 3) set the parameter vector for transformation '''
    parameter_vector = sitk.VectorOfParameterMap()  # init
    map_translation = get_translation_map() # get map
    map_rigid = get_rigid_map(is_mask) 
    # map_affine = get_affine_map(is_mask)
    # map_bspline = get_bspline_map(is_mask)
    parameter_vector.append(map_translation) # set parameter vector
    parameter_vector.append(map_rigid)
    # parameter_vector.append(map_affine)
    # parameter_vector.append(map_bspline)

    ''' 4) transform with parameter vector'''
    elastix_img_filter.SetParameterMap(parameter_vector)
    if is_mask:
        elastix_img_filter.SetParameter("MaximumNumberOfSamplingAttempts",'100')
        elastix_img_filter.SetParameter("RequiredRatioOfValidSamples", '0.05')
        # elastixImageFilter.SetParameter("ImageSampler", 'RandomSparseMask')
    elastix_img_filter.Execute()

    ''' 5) save parameter map '''
    sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[0], map_translate_path)
    sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[1], map_rigid_path)
    # sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[2], map_affine_path)        
    # sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[3], map_bspline_path)        
        
   
    ''' 6) save Nifti Image which has been transformed'''
    result_image = elastix_img_filter.GetResultImage()
    result_image = sitk.Cast(result_image, sitk.sitkUInt8)
    header_nii_path = '/data/Nifti/In/FOV_66/OCT_Resized/10001_oct_fov66_original.nii.gz'
    header_image = sitk.ReadImage(header_nii_path, sitk.sitkUInt8)
    result_image.SetSpacing(header_image.GetSpacing())
    result_image.SetOrigin(header_image.GetOrigin())
    result_image.SetDirection(header_image.GetDirection())
    sitk.WriteImage(result_image, mov_after_path)

    print(f'\r{kind:>4} : {subject} has been transformed.', end='')

def use_parameter_map(subject, move_before_dir, move_after_dir, parameter_dir, is_mask=False):
    ''' 1) set the path '''
    kind = 'mask' if 'VolMask' in move_before_dir else 'octa' if 'OCTA' in move_before_dir else 'oct'
    os.makedirs(move_after_dir, exist_ok=True)
    before_path = os.path.join(move_before_dir, f'{subject}.nii.gz')
    after_path = os.path.join(move_after_dir, f'{subject}_{kind}_translate_rigid.nii.gz')

    ''' 2) read paramters from saved .txt files & set parameter vector'''
    map_path_translate = os.path.join(parameter_dir,f'{subject}_translate.txt')
    map_path_rigid = os.path.join(parameter_dir,f'{subject}_rigid.txt')
    # map_path_affine = os.path.join(parameter_dir,f'{subject}_affine.txt')
    # map_path_bspline = os.path.join(parameter_dir,f'{subject}_bspline.txt')
    parameter_path = [map_path_translate, map_path_rigid]
    # parameter_path = [map_path_translate, map_path_rigid, map_path_affine]
    parameter_vector = sitk.VectorOfParameterMap()
    transform_img_filter = sitk.TransformixImageFilter()
    transform_img_filter.LogToConsoleOff()

    for p in parameter_path:
        parameter_map = sitk.ReadParameterFile(p)
        if is_mask:
            parameter_map['FinalBSplineInterpolationOrder']=['0']
        parameter_vector.append(parameter_map)
    

    """2) read moving mage"""
    move = sitk.ReadImage(before_path, sitk.sitkUInt8)
    transform_img_filter.SetMovingImage(move)

    """3) transform with parameter vector"""
    transform_img_filter.SetTransformParameterMap(parameter_vector)
    transform_img_filter.Execute()
    result_image = transform_img_filter.GetResultImage()

    """4) type casting : Float32 -> uInt8"""
    result_image = sitk.Cast(result_image, sitk.sitkUInt8)

    """5) save casted Image"""
    if 'FOV_66' in move_before_dir:
        header_nii_path = '/data/Nifti/In/FOV_66/OCT_Resized/10001_oct_fov66_original.nii.gz'
    else:
        header_nii_path = '/data/Nifti/In/FOV_33/OCT_Resized/10334_oct_fov33_original.nii.gz'
    header_image = sitk.ReadImage(header_nii_path, sitk.sitkUInt8)
    result_image.SetSpacing(header_image.GetSpacing())
    result_image.SetOrigin(header_image.GetOrigin())
    result_image.SetDirection(header_image.GetDirection())
    sitk.WriteImage(result_image, after_path)
    print(f'\r{kind:>4} : {subject} has been transformed.')


def main():
    reference_path = {'FOV66' : '/data/Nifti/In/FOV_66/VolMask/10132.nii.gz',#'/data/Nifti/In/FOV_66/OCT/10132.nii.gz',
                      'FOV33' : '/data/Nifti/In/FOV_33/OCT/10334.nii.gz'}

    subject_list = {'FOV66' : [s for s in range(10001, 10301)],
                    'FOV33' : [s for s in range(10301, 10501)]}

    oct_dir = {'FOV66' : {'before' : '/data/Nifti/In/FOV_66/OCT/',
                          'after' : '/data/Nifti/In/Transformed/FOV_66/OCT'},                          
               'FOV33' : {'before' : '/data/Nifti/In/FOV_33/OCT/',
                          'after' : '/data/Nifti/In/Transformed/FOV_33/OCT'}}

    octa_dir = {'FOV66' : {'before' : '/data/Nifti/In/FOV_66/OCTA/',
                           'after' : '/data/Nifti/In/FOV_66/Transformed/OCTA'},
                'FOV33' : {'before' : '/data/Nifti/In/FOV_33/OCTA/',
                           'after' : '/data/Nifti/In/Transformed/FOV_33/OCTA'}}

    mask_dir = {'FOV66' : {'before' : '/data/Nifti/In/FOV_66/VolMask',
                           'after' : '/data/Nifti/In/Transformed/FOV_66/VolMask/'},
                'FOV33' : {}}

    map_dir = {'FOV66' : '/data/Nifti/In/FOV_66/Parameter',
               'FOV33' : '/data/Nifti/In/FOV_33/Parameter'}

    # for subject_idx in subject_list['FOV66']:
    #     get_parameter_map(fix_path = reference_path['FOV66'], 
    #                       subject = subject_idx, 
    #                       move_before_dir = mask_dir['FOV66']['before'], 
    #                       move_after_dir = mask_dir['FOV66']['after'], 
    #                       parameter_dir = map_dir['FOV66'], 
    #                       is_mask=True)

    #     use_parameter_map(subject = subject_idx, 
    #                       move_before_dir = oct_dir['FOV66']['before'], 
    #                       move_after_dir = oct_dir['FOV66']['after'], 
    #                       parameter_dir = map_dir['FOV66'], 
    #                       is_mask=True)

    #     use_parameter_map(subject = subject_idx, 
    #                       move_before_dir = octa_dir['FOV66']['before'], 
    #                       move_after_dir = octa_dir['FOV66']['after'], 
    #                       parameter_dir = map_dir['FOV66'], 
    #                       is_mask=True)

    for subject_idx in subject_list['FOV33']:
        get_parameter_map(fix_path = reference_path['FOV33'], 
                          subject = subject_idx, 
                          move_before_dir = oct_dir['FOV33']['before'], 
                          move_after_dir = oct_dir['FOV33']['after'], 
                          parameter_dir = map_dir['FOV33'], 
                          is_mask=True)
        
        use_parameter_map(subject = subject_idx, 
                          move_before_dir = octa_dir['FOV33']['before'], 
                          move_after_dir = octa_dir['FOV33']['after'], 
                          parameter_dir = map_dir['FOV33'], 
                          is_mask=True)
        
        # use_parameter_map(subject = subject_idx, 
        #                   move_before_dir = mask_dir['FOV66']['before'], 
        #                   move_after_dir = mask_dir['FOV66']['after'], 
        #                   parameter_dir = map_dir['FOV66'], 
        #                   is_mask=True)



main()