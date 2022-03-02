import os 
import numpy as np
import nibabel as nib

def load_nifti(patient, nii_dir):
    try:
        nifti_path = os.path.join(nii_dir, f'{patient}.nii.gz')
        return nib.load(nifti_path)
    except:
        nifti_path = os.path.join(nii_dir, f'{patient}.nii')
        print('nii file has been loaded. it is recommended to compress to .nii.gz.')
        return nib.load(nifti_path)

def crop_nifti(data_dir, mask_dir, patient, center):
    total_height = 256
    save_dir = f'/data/Nifti/In/Transformed/OCTA_SRL_{total_height}'
    save_dir_mask = f'/data/Nifti/In/Transformed/Mask_SRL_{total_height}' 

    nii = load_nifti(patient, data_dir)
    nii_arr = np.asarray(nii.dataobj)
    nii_cropped = nii_arr[:, center-int(total_height/2):center+int(total_height/2), :]
    nii_cropped_img = nib.Nifti1Image(np.uint8(nii_cropped), nii.affine, nii.header)
    os.makedirs(save_dir, exist_ok=True)
    nib.save(nii_cropped_img, os.path.join(save_dir, f'{patient}.nii.gz'))
    print(f"{patient} has been cropped. size: {nii_cropped.shape}")


    mask_nii = load_nifti(patient, mask_dir)
    mask_nii_arr = np.asarray(mask_nii.dataobj)
    mask_srl_nii_arr = np.zeros((192, total_height, 192))
    mask_nii_cropped = mask_nii_arr[:, center-int(total_height/2):center+int(total_height/2), :]
    mask_srl_nii_arr[np.where((1<=mask_nii_cropped)&(mask_nii_cropped<=4))] = 1
    mask_srl_cropped_img = nib.Nifti1Image(mask_nii_cropped, mask_nii.affine, mask_nii.header)

    os.makedirs(save_dir_mask, exist_ok=True)
    nib.save(mask_srl_cropped_img, os.path.join(save_dir_mask, f'{patient}.nii.gz'))
    print(f"{patient} has been cropped. size: {mask_nii_cropped.shape}")

def check_height(patient_id, data_dir):
    # rename_file(select_dir)
    patient = patient_id
    patients.append(patient)
    srl = load_nifti(patient_id, nii_dir=data_dir)
    srl_nii = np.asarray(srl.dataobj)
    if np.max(srl_nii)==0:
        pass
    else:
        for x in range(srl_nii.shape[0]):
            for y in range(srl_nii.shape[2]):
                if np.sum(srl_nii[x,:,y].nonzero()) != 0:
                    lower = np.min(srl_nii[x,:,y].nonzero())
                    upper = np.max(srl_nii[x,:,y].nonzero())
                    center = int((lower+upper)/2)
                    height = upper-lower
                    patients_dict[patient]['up'].append(upper)
                    patients_dict[patient]['bottom'].append(lower)
                    patients_dict[patient]['height'].append(height)
                    patients_dict[patient]['center'].append(center)
            
        maxH = np.max(patients_dict[patient]['height'])
        maxU = np.max(patients_dict[patient]['up'])
        minB = np.min(patients_dict[patient]['bottom'])
        center_z_idx = int(np.median(patients_dict[patient]['center']))
        need_height = int(np.abs(maxU-center_z_idx)+np.abs(center_z_idx-minB))
        patients_dict[patient]['needed_height'].append(need_height)

        print(f'{patient} max non-zero index : {maxU}')
        print(f'{patient} min non-zero index : {minB}')
        print(f'{patient} max height index : {maxH}')
        print(f'{patient} center index of z-axis : {center_z_idx}' )
        print(f'{patient} need {patients_dict[patient]["needed_height"][0]} height.')
        
        mask_dir = '/data/Nifti/In/Transformed/VolMask'
        crop_nifti(data_dir, mask_dir, patient, center_z_idx)

def dict_to_CSV(save_dir, save_name):
    import pandas as pd
    save_name = 'volume_info.csv'
    df_path = os.path.join(save_dir, save_name)
    
    height_list = [np.max(patients_dict[p]['height']) for p in patients]
    bottom_list = [np.min(patients_dict[p]['bottom']) for p in patients]
    up_list     = [np.max(patients_dict[p]['up']) for p in patients]
    center_list = [int(np.mean(patients_dict[p]['center'])) for p in patients]
    needed_height_list = [patients_dict[p]['needed_height'][0] for p in patients]
    
    df = pd.DataFrame({'patient': patients, 
                       'height':height_list,
                       'bottom':bottom_list,
                       'up':up_list, 
                       'center':center_list,
                       'needed_height':needed_height_list})

    df.to_csv(df_path, index=True, index_label='idx', mode='w')

def file_name_change(patient, before_dir, after_dir):
    fov = 'fov66' if patient < 10301 else 'fov33'
    before_path = os.path.join(before_dir, f'{patient}_mask_{fov}_resized.nii.gz')
    after_path = os.path.join(after_dir, f'{patient}.nii.gz')

    os.system(f'mv {before_path} {after_path}')
    print(f'{patient} has been re-named.')

def main():
    global patients_dict, data_dir, skip_list, patients
    patients = []
    # data_dirs = get_dir_lab()
    skip_list = [10035, 10057, 10114, 10219, 10220]
    select = [patient for patient in range(10001, 10501)]
    # broken = [10219, 10220]
    # patients_dict = {}
    patients_dict = {p : {'up':[],'bottom':[],'center':[],'height':[], 'needed_height':[]} for p in select}    

    data_dirs = '/data/Nifti/In/Transformed/OCTA_SRL'
    crop_dir ='/data/Nifti/In/Transformed/OCTA_SRL_cropped'
    os.makedirs(crop_dir, exist_ok=True)
    for patient in select:
        # if patient not in skip_list:

        # before_dir = '/data/Nifti/In/Transformed/VolMask'
        # after_dir = before_dir
        # file_name_change(patient, before_dir, after_dir)

        check_height( patient_id=patient, 
                      data_dir=data_dirs)

    # dict_to_CSV(save_dir=crop_dir, save_name='volume_info.csv')
    
                    

main()
