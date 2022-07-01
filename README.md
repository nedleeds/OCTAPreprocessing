
# OCTAPreprocessing

> Basically, here are 2 main process for the OCT(A) volume data.
> First one is making volume data(.nii.gz) from the provided image(.bmp).
> Second one is transforming and resizing the Nifti data(linear registraion, crop&resize and resize nifti).

### 1. Make a Nifti volume by stacking bmp Images

####   bmp2nii.py

- Convert Bmp files to Nifti files.Set 3 types of options.

  1. bmp_dir - load directory

     - consists of bmp files of OCT or OCTA image.
     - directory structure should be like below
     - bmp directory name should include OCT, OCTA.
  2. nii_dir - save directory
  3. FOV (Field Of View for scanning)

     - physical resolution = FOV size * scale
     - orgin, spacing will be setted by this FOV and scale factor.

### 2. Transform the Nifti Volume

#### 2-1) registration.py

#### 2-2) crop_resize.py
