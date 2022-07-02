# OCTAPreprocessing

> Basically, here are 2 main process for the OCT(A) volume data
> First, reconstruct 3D raw volume data by stacking .bmp images
> Second, transform and resize the reconstructed raw data(linear registraion, crop&resize and resize nifti).
> The reason of these process is really clear. In the process of scanning, it is dificult to
> prevent all the movement from the patients. Especially the OCT data is a retina image,
> it is almost nonsense that we can control our pupil movement.
> And the data consists of left and right eyes, partially, it has structural differences.
> To deal with these points, we propose below data pre-processing steps.

### 1. Make a Nifti volume by stacking bmp Images

* ### [bmp2nii.py](https://github.com/nedleeds/OCTAPreprocessing/blob/main/bmp2nii.py#L9)

- Convert Bmp files to Nifti files and set the 3 types of options.

  1. bmp_dir - load directory

     - consists of bmp files of OCT or OCTA image.
     - directory structure should be like below
     - bmp directory name should include OCT, OCTA.
  2. nii_dir - save directory
  3. FOV (Field Of View for scanning)

     - physical resolution = [FOV size * scale](https://github.com/nedleeds/OCTAPreprocessing/blob/main/bmp2nii.py#L82)
     - orgin, spacing will be setted by this FOV and scale factor.
     - This figure needs to [set the header information of the Nifti](https://github.com/nedleeds/OCTAPreprocessing/blob/main/bmp2nii.py#L56).
     - source : [IEEE-OCTA500](https://ieee-dataport.org/open-access/octa-500)

### 2. Transform the Nifti Volume

> Transformation consists of several setps and overall process is shown in below Figure.

![preprocessing_3d](https://user-images.githubusercontent.com/48194000/176991330-8f9d3f5a-e639-4acc-b6e6-f078e7cb6e54.png)

* Retina Layer segmentation

  * This part had been implemented by [OCTExplorer3.8.0](https://www.iibi.uiowa.edu/ophthalmic-analysis)
* [registration.py](https://github.com/nedleeds/OCTAPreprocessing/blob/main/registration.py#L212)

  * In this experiment, to retain the volumetric data and try not to give a damage to the original data,
    only [linear registration (translation, affine transformaion) had been leveraged](https://github.com/nedleeds/OCTAPreprocessing/blob/main/registration.py#L125).
  * However, we implemented the non-linear transformation either, you can use it if you want.
  * The library that we have used for registration is [SimpleITK](https://simpleitk.org/) and you can install easily like below :
    * ```python
      pip install SimpleITK
      pip install SimpleITK-SimpleElastix
      ```
* [resize_nifti.py]()

  * The given data had been collected with different FOV, it has different resolution. To utilize the total data(500), it is needed to implement Volume resizing.
  * [For FOV66(subject - 10001 ~ 10300), center-cropping has been used to match the FOV33 but as its size still 200x200x640, considering the pooling step for train-phase, we resize it to 192x192x640.](https://github.com/nedleeds/OCTAPreprocessing/blob/main/resize_nifti.py#L213)
  * [For FOV33(subject - 10301 ~ 10500), only the resizing had been adapted.](https://github.com/nedleeds/OCTAPreprocessing/blob/main/resize_nifti.py#L217)
  * [crop_resize.py](https://github.com/nedleeds/OCTAPreprocessing/blob/main/crop_resize.py) is for the 2D. As 2D Enface has also different FOV, resizing is also needed either.


* [check_volume.py](https://github.com/nedleeds/OCTAPreprocessing/blob/main/check_volume.py#L68)
  * This script is for checking the height of all the volumes by considering non-zero value for the z-axis.
    * Procedure

      > 1. Check one-by-one and save the each first and last non-zero values.
      > 2. Before finish checking, save these z-indices for the .csv file.
      > 3. Choose the proper height based on the .csv file.
      > 4. Re-implement this module with the selected height.
      > 5. Then volume will be cropped from the middle point of the non-zero z indices
      >    with the selected height automatically.
      >
