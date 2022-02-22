# OCTPreprocessin

### Bmp2Nifti

- Convert Bmp files to Nifti files.Set 3 types of options.

  1. bmp_dir - load directory

     - consists of bmp files of OCT or OCTA image.
     - directory structure should be like below.
       ├── OCT
       │   	├── 10001
       │   	│   	├── 1.bmp
       │   	│   	├── 2.bmp
       │   	│   	├── 3.bmp
       │   	│   	├──     ...
       │   	│   	└── 400.bmp
       │   	├── 10002
       │   	└──    ...
       └── OCTA
       ├── 10301
       ├── 10302
       └──    ...
     - bmp directory name should include OCT, OCTA.
  2. nii_dir - save directory
  3. FOV (Field Of View for scanning)

     - physical resolution = FOV size * scale
     - orgin, spacing will be setted by this FOV and scale factor.

### NiftiResize
