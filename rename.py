import os
import shutil
import glob

NIBPATH = "/root/Share/data/nii/nib"
NIIPATH = "/root/Share/data/nii"

for i in os.listdir(NIBPATH):
    # print(i.split('.')[0][:5])
    print(i)
    num = i.split('.')[0][:5]
    # os.rename(i, f"{num}.nii.gz")
    shutil.move(os.path.join(NIBPATH,i), os.path.join(NIIPATH, f"{num}.nii.gz"))