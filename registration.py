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

def get_parameter_map(fix_path, subject, mov_before_dir, mov_after_dir, parameter_dir, is_mask=False):
    os.makedirs(mov_after_dir, exist_ok=True)
    os.makedirs(parameter_dir, exist_ok=True)

    mov_before_path = os.path.join(mov_before_dir, f'{subject}.nii.gz')
    mov_after_path = os.path.join(mov_after_dir, f'{subject}.nii.gz')

    map_translate_path = os.path.join(parameter_dir, f'{subject}_translate.txt')
    map_rigid_path = os.path.join(parameter_dir, f'{subject}_rigid.txt')
    # map_affine_path = os.path.join(parameter_dir, f'{subject}_affine.txt')
    # map_bspline_path = os.path.join(parameter_dir, f'{subject}_bspline.txt')

    #### Init Elastix filter and set the fix and moving image. ####
    elastix_img_filter = sitk.ElastixImageFilter()
    elastix_img_filter.LogToConsoleOn()
    elastix_img_filter.SetFixedImage(sitk.ReadImage(fix_path, sitk.sitkUInt8))
    elastix_img_filter.SetMovingImage(sitk.ReadImage(mov_before_path, sitk.sitkUInt8))

    #### Set the parameter vector for transformation ####
    parameter_vector = sitk.VectorOfParameterMap()

    map_translation = get_translation_map()
    map_rigid = get_rigid_map(is_mask)
    # map_affine = get_affine_map(is_mask)
    # map_bspline = get_bspline_map(is_mask)
    
    parameter_vector.append(map_translation)
    parameter_vector.append(map_rigid)
    # parameter_vector.append(map_affine)
    # parameter_vector.append(map_bspline)

    #### Do Transform ####
    elastix_img_filter.SetParameterMap(parameter_vector)
    if is_mask:
        elastix_img_filter.SetParameter("MaximumNumberOfSamplingAttempts",'100')
        elastix_img_filter.SetParameter("RequiredRatioOfValidSamples", '0.05')
        # elastixImageFilter.SetParameter("ImageSampler", 'RandomSparseMask')
    elastix_img_filter.Execute()

    #### Save ParameterMap ####
    sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[0], map_translate_path)
    sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[1], map_rigid_path)
    # sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[2], map_affine_path)        
    # sitk.WriteParameterFile(elastix_img_filter.GetTransformParameterMap()[3], map_bspline_path)        
        
   # Save path
    # Save Nifti Image which is transformed
    result_image = elastix_img_filter.GetResultImage()
    result_image = sitk.Cast(result_image, sitk.sitkUInt8)
    header_nii_path = '/data/Nifti/In/FOV_66/OCT_Resized/10001_oct_fov66_original.nii.gz'
    header_image = sitk.ReadImage(header_nii_path, sitk.sitkUInt8)
    result_image.SetSpacing(header_image.GetSpacing())
    result_image.SetOrigin(header_image.GetOrigin())
    result_image.SetDirection(header_image.GetDirection())
    sitk.WriteImage(result_image, mov_after_path)

    print(f'{subject} paramters are saved at {parameter_dir}.')

def main():
    reference_path = {'FOV66' : '/data/Nifti/In/FOV_66/OCT/10132.nii.gz',
                      'FOV33' : '/data/Nifti/In/FOV_33/OCT/10334.nii.gz'}

    subject_list = [s for s in range(10001, 10301)]

    oct_dir = {'FOV66' : {'before' : '/data/Nifti/In/FOV_66/OCT/',
                          'after' : '/data/Nifti/In/FOV_66/OCT_Transformed/'},                          
               'FOV33' : {'before' : '/data/Nifti/In/FOV_33/OCT/',
                          'after' : '/data/Nifti/In/FOV_33/OCT_Transformed/'}}

    octa_dir = {'FOV66' : {'before' : '/data/Nifti/In/FOV_66/OCTA/',
                           'after' : '/data/Nifti/In/FOV_66/OCTA_Transformed/'},                          
                'FOV33' : {'before' : '/data/Nifti/In/FOV_33/OCTA/',
                           'after' : '/data/Nifti/In/FOV_33/OCTA_Transformed/'}}

    map_dir = {'FOV66' : '/data/Nifti/In/FOV_66/Parameter',
               'FOV33' : '/data/Nifti/In/FOV_33/Parameter'}

    for subject_idx in subject_list:
        get_parameter_map(fix_path = reference_path['FOV66'], 
                          subject = subject_idx, 
                          mov_before_dir = oct_dir['FOV66']['before'], 
                          mov_after_dir = oct_dir['FOV66']['after'], 
                          parameter_dir = map_dir['FOV66'], 
                          is_mask=False)

main()