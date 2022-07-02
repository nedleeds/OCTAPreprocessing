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

     - physical resolution = FOV size * scale
     - orgin, spacing will be setted by this FOV and scale factor.
     - This figure needs to set the header information of the Nifti.
     - source : [IEEE-OCTA500](https://ieee-dataport.org/open-access/octa-500)

### 2. Transform the Nifti Volume

#### 2-1) registration.py

#### 2-2) crop_resize.py
