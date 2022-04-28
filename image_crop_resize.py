import os
import cv2
from matplotlib import pyplot as plt
import numpy as np
import nibabel as nib
from PIL import Image, ImageDraw
   
def image_resize(load_image_path, save_image_path, resized_size, is_display):
    img = Image.open(load_image_path) 

    # resized_img = img.resize(resized_size, Image.LANCZOS)
    img.save(save_image_path,"PNG")
    
    # if is_display:
    #     resized_img.show()

def image_crop(load_image_path, save_image_path, crop_area_path, cropped_size, is_display):
    img = Image.open(load_image_path) 
    img_arr = np.asarray(img)
    
    old_row, old_col = img_arr.shape
    new_row, new_col = cropped_size
    
    cropped_img_arr = img_arr[ new_row // 2 : old_row - (new_row // 2), 
                               new_col // 2 : old_col - (new_col // 2) ]
    
    cropped_img = Image.fromarray(np.uint8(cropped_img_arr))
    # cropped_img.save(save_image_path, format='png')
    
    # draw & save crop area
    before_image = Image.open(load_image_path).convert('RGB')
    draw_filter = ImageDraw.Draw(before_image)
    draw_filter.rectangle((new_row//2, new_row//2, old_row-(new_row//2), old_row-(new_row//2)), outline='red', width = 3)
    # before_image.show()
    before_image.save(crop_area_path, format='png')

    if is_display:
        cropped_img.show()

def make_enface(load_nifti_path, load_mask_path, save_enface_path):
    nii_img_og = nib.load(load_nifti_path)
    nii_arr = np.asarray(nii_img_og.dataobj)
    mask_arr = np.asarray(nib.load(load_mask_path).dataobj)
    
    srl_arr = np.zeros(np.shape(nii_arr))
    srl_arr[(0<mask_arr) & (mask_arr<5)] = nii_arr[(0<mask_arr) & (mask_arr<5)]

    srl_pruned = np.zeros(np.shape(srl_arr))
    lower = np.percentile(srl_arr[np.where(mask_arr > 0)], 0)
    upper = np.percentile(srl_arr[np.where(mask_arr > 0)], 99.97)
    srl_pruned[(lower <= srl_arr) & (srl_arr <= upper)] = srl_arr[(lower <= srl_arr) & (srl_arr <= upper)]
    
    m = np.min(srl_pruned)
    M = np.max(srl_pruned)
    srl_pruned = np.uint8((srl_pruned - m) / (M - m)*255)

    nii_enface = np.max(srl_pruned, axis=1)
    nii_enface = np.rot90(nii_enface)

    nii_img = Image.fromarray(np.uint8(nii_enface))
    nii_img.save(save_enface_path, format='png')
    

def make_bscan(load_nifti_path, save_bscan_path, slice_num, is_superficial=None):
    nii_img = nib.load(load_nifti_path)
    nii_arr = nii_img.dataobj
    
    nii_arr = np.transpose(nii_arr, (0,2,1))
    nii_new = np.zeros(np.shape(nii_arr))

    for idx in range(np.shape(nii_arr)[-1]):
        nii_new[:,:,idx] = np.rot90(nii_arr[:,:,idx], k=3)

    if slice_num is None:
        slice_num = np.shape(nii_arr)[0]//2
    
    nii_bscan = nii_new[slice_num,:,:]
    if is_superficial:
        nii_bscan_srl = np.zeros(np.shape(nii_bscan))
        nii_bscan_srl[(nii_bscan>0) & (nii_bscan<5)] = nii_bscan[(nii_bscan>0) & (nii_bscan<5)]
        nii_bscan = nii_bscan_srl
        
    m = np.min(nii_bscan)
    M = np.max(nii_bscan)
    
    nii_bscan = np.uint8((nii_bscan-m)/(M-m)*255)
    nii_bscan = np.rot90(nii_bscan, k=3)

    nii_bscan_img = Image.fromarray(nii_bscan)
    nii_bscan_img.save(save_bscan_path, format='png')

def get_FOV33_info(nii_size):
    scale = 19*3
    fov33_size = (3, 2, 3)  # fov66_size = (6, 6, 2)
    resolution = [(f*scale) for f in fov33_size]
    spacing = [(r/v) for r,v in zip(resolution, nii_size)]
    origin = [-r/2 for r in resolution]

    new_info = {'pixel' : nii_size,
                'origin' : origin,
                'spacing': spacing}

    return new_info

def save_nifti(nifti_data, before_info, after_info, save_path):
    w_pix, h_pix, d_pix = after_info['pixel']
    w_spacing, h_spacing, d_spacing = after_info['spacing']
    w_origin, h_origin, d_origin = after_info['origin']

    nifti_info_new = before_info
    nifti_info_new['dim'] = [3, w_pix, h_pix, d_pix, 1, 1, 1, 1]
    nifti_info_new['xyzt_units'] = 0
    nifti_info_new['pixdim'] = [1., w_spacing, h_spacing, d_spacing, 1., 1., 1., 1.]
    nifti_info_new['qoffset_x'] = -w_origin
    nifti_info_new['qoffset_y'] = -h_origin
    nifti_info_new['qoffset_z'] = d_origin
    nifti_info_new['srow_x'] = [-w_spacing, 0, 0, -w_origin]
    nifti_info_new['srow_y'] = [0, -h_spacing, 0, -h_origin]
    nifti_info_new['srow_z'] = [0, 0,  d_spacing,  d_origin]

    nifti_new_img = nib.Nifti1Image(np.uint8(nifti_data), nifti_info_new.get_best_affine())
    nib.save(nifti_new_img, save_path, )

    print(f'nifti saved at {save_path}')

def extract_patch(load_image_path):
    from sklearn.feature_extraction import image

    img = Image.open(load_image_path)
    img_arr = np.asarray(img)[:,:,0]
    img_size = img_arr.shape
    patch_num = 4
    row_size, col_size = (int(img_size[0]//np.sqrt(patch_num)), int(img_size[1]//np.sqrt(patch_num)))
    
    img_1 = img_arr[0:row_size, 0:col_size]
    img_2 = img_arr[row_size: , 0:col_size]
    img_3 = img_arr[0:row_size, col_size:]
    img_4 = img_arr[row_size: , col_size:]

    pil_img_1 = Image.fromarray(np.uint8(img_1))
    pil_img_2 = Image.fromarray(np.uint8(img_2))
    pil_img_3 = Image.fromarray(np.uint8(img_3))
    pil_img_4 = Image.fromarray(np.uint8(img_4))
    
    pil_img_1_resized = pil_img_1.resize((100, 100), Image.NEAREST)
    pil_img_2_resized = pil_img_2.resize((100, 100), Image.NEAREST)
    pil_img_3_resized = pil_img_3.resize((100, 100), Image.NEAREST)
    pil_img_4_resized = pil_img_4.resize((100, 100), Image.NEAREST)
    
    print()

def main():
    # subjects = [ i for i in range(10001,10501) ]

    subjects = [10132, 10334]#, 10334]
    subjects.extend([i for i in range(10001, 10501, 50)])
    subjects = [i for i in range(10001, 10501)]

    before_registered_dir = {'mask':'/data/Nifti/In/Before_Transformed/VolMask',
                             'octa':'/data/Nifti/In/Before_Transformed/OCTA',
                             'oct' :'/data/Nifti/In/Before_Transformed/OCT'}

    after_registered_dir = {'mask':'/data/Nifti/In/Transformed/VolMask_reg',
                            'octa':'/data/Nifti/In/Transformed/OCTA',
                            'oct' :'/data/Nifti/In/Transformed/OCT'} # 10001_mask_translate_rigid.nii.gz
    
    after_crop_resize_dir = {'octa' : '/data/Nifti/In/Transformed/OCTA_Crop_Resize',
                             'mask' : '/data/Nifti/In/Transformed/Mask_Crop_Resize'}

    final_dir = {'octa' : '/data/Nifti/In/Transformed/OCTA_SRL_256',
                 'mask' : '/data/Nifti/In/Transformed/Mask_SRL_256'}

    bscan_dir = {'mask':'/data/Nifti/In/Transformed/Bscan/VolMask',
                 'octa':'/data/Nifti/In/Transformed/Bscan/OCTA',
                 'oct' :'/data/Nifti/In/Transformed/Bscan/OCT'} # 10001_mask_translate_rigid.nii.gz

    rename_dir = '/data/Nifti/In/Transformed/OCTA_SRL_256_V2'
    image_dir ='/data/Nifti/In/Transformed/OCTA_SRL_EnFace'
    for subject in subjects:
        load_img_path = os.path.join(image_dir, f'{subject}.png')
        # extract_patch(load_image_path = load_img_path)
        
        image_resize(load_image_path = os.path.join('/data/dataset/OCTA-500/OG', f'{subject}.bmp'), 
                     save_image_path = os.path.join('/data/dataset/OCTA-500/OG', f'{subject}.png'),
                     resized_size = (192, 192), 
                     is_display = False)


        # load_nii_path = os.path.join(final_dir['octa'], f'{subject}.nii.gz')
        # mask_nii_path = os.path.join(final_dir['mask'], f'{subject}.nii.gz')
        # make_enface(load_nifti_path = load_nii_path, 
        #             load_mask_path = mask_nii_path,
        #             save_enface_path = f'/data/Nifti/In/Transformed/EnFace/{subject}_final.png',
        #             subject = subject)
                    
        # ### Bscan - for Z Axis C 
        # load_dir = '/data/Nifti/In/Transformed/Mask_SRL_256'
        # load_path = os.path.join(load_dir, f'{subject}.nii.gz')
        # bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_mask_reg_resize_zcrop.png')

        # make_bscan(load_nifti_path = load_path,
        #            save_bscan_path = bscan_path,
        #            slice_num = 192//2)

        # ### Bscan - for Crop & Resize Result from FOV 3x3            
        # load_dir = '/data/Nifti/In/Transformed/FOV_33/Mask_192'
        # resized_path = os.path.join(load_dir, f'{subject}_mask_fov33_resized.nii.gz')

        # make_bscan(load_nifti_path = resized_path,
        #            save_bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_reg_resized.png'),
        #            slice_num = 192//2)

        # ### Bscan - for Crop & Resize Result from FOV 6x6
        # if subject<10301:
        #     load_dir = '/data/Nifti/In/Transformed/FOV_66/Mask_192'
        #     cropped_path = os.path.join(load_dir, f'{subject}_mask_fov66_cropped.nii.gz')
        #     resized_path = os.path.join(load_dir, f'{subject}_mask_fov66_resized.nii.gz')
        # else:
        #     load_dir = '/data/Nifti/In/Transformed/FOV_33/Mask_192'
        #     cropped_path = os.path.join(load_dir, f'{subject}_mask_fov33_cropped.nii.gz')
        #     resized_path = os.path.join(load_dir, f'{subject}_mask_fov33_resized.nii.gz')

        

        # make_bscan(load_nifti_path = cropped_path,
        #            save_bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_reg_crop.png'),
        #            slice_num = 200//2)

        # make_bscan(load_nifti_path = resized_path,
        #            save_bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_reg_crop_resize.png'),
        #            slice_num = 192//2)

        # make_bscan(load_nifti_path = resized_path,
        #            save_bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_reg_crop_resize_srl.png'),
        #            slice_num = 192//2,
                #    is_superficial = True)

        '''
        # These parts are for making bscan - for before & after registration
        slice_num = 400//2 if subject<10301 else 304//2

        make_bscan(load_nifti_path = os.path.join(before_registered_dir['mask'],f'{subject}.nii.gz'),
                   save_bscan_path = os.path.join(bscan_dir['mask'],f'{subject}_reg_before.png'),
                   slice_num = slice_num)

        make_bscan(load_nifti_path = os.path.join(after_registered_dir['mask'],f'{subject}_mask_translate_rigid.nii.gz'),
                   save_bscan_path = os.path.join(bscan_dir['mask'],f'{subject}_reg_after.png'),
                   slice_num = slice_num)
        '''


        '''
        #### These parts are for the Crop & Resizing 2D ground truth projected Image ####
        if subject < 10301:
            before_crop_dir = '/data/dataset/OCTA-500/OCTA_6M/Projection Maps/OCTA(ILM_OPL)'
            after_crop_dir = '/data/dataset/OG/OCTA_Enface'
            crop_area_dir = '/data/dataset/OG/OCTA_Enface_with_crop_area'
            os.makedirs(crop_area_dir, exist_ok=True)

            #### Make En Face Image ####
            make_enface(load_nifti_path=f'/data/Nifti/In/FOV_66/OCTA_srl/{subject}.nii.gz',
                        save_enface_path=f'/home/dhl/Project/OCTPreprocessing/enface/{subject}.png')

            #### Crop 2D Image ####
            image_crop(load_image_path = os.path.join(before_crop_dir, f'{subject}.bmp'),
                       save_image_path = os.path.join(after_crop_dir, f'{subject}.png'),
                       crop_area_path = os.path.join(crop_area_dir,f'{subject}.png'),
                       cropped_size = (200, 200),
                       is_display = False)

            #### Resize 2D Image ####
            image_resize(load_image_path = os.path.join(after_crop_dir, f'{subject}.png'), 
                         save_image_path = os.path.join(after_crop_dir, f'{subject}.png'),
                         resized_size = (192, 192), 
                         is_display = False)

        else:
            before_resize_dir = '/data/dataset/OCTA-500/OCTA_3M/Projection Maps/OCTA(ILM_OPL)'
            after_resize_dir = '/data/dataset/OCTA_Enface'
            image_resize(load_image_path = os.path.join(before_resize_dir, f'{subject}.bmp'), 
                         save_image_path = os.path.join(after_resize_dir, f'{subject}.png'),
                         resized_size = (192, 192), 
                         is_display = False)

        '''

        print(f'{subject} has been saved.')

main()