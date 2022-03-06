import os
import cv2
from matplotlib import pyplot as plt
import numpy as np
import nibabel as nib
from PIL import Image, ImageDraw
   
def image_resize(load_image_path, save_image_path, resized_size, is_display):
    img = Image.open(load_image_path) 

    resized_img = img.resize(resized_size, Image.LANCZOS)
    resized_img.save(save_image_path,"PNG")
    
    if is_display:
        resized_img.show()

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

def make_enface(load_nifti_path, save_enface_path):
    nii_img = nib.load(load_nifti_path)
    nii_arr = nii_img.dataobj
    nii_info = nii_img.header

    nii_enface = np.max(nii_arr, axis=1)
    nii_enface = np.rot90(nii_enface)

    imgray = cv2.cvtColor(nii_enface, cv2.COLOR_RGB2BGR)
    cv2.imshow(imgray)
    # ret, thr = cv2.threshold(imgray, 10, 255, cv2.THRESH_BINARY)

    # detector = cv2.SimpleBlobDetector()
    # keypoints = detector.detect(Image.fromarray(np.uint8(thr)).convert("RGB"))
    # im_with_keypoints = cv2.drawKeypoints(imgray, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # np.min(thr)

    # contours, hierarchy = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # img_contours = np.zeros(imgray.shape)
    # cv2.drawContours(img_contours, contours, -1, (0,255,0), 3)
    # cv2.imshow(img_contours)

def make_bscan(load_nifti_path, save_bscan_path, slice_num):
    nii_img = nib.load(load_nifti_path)
    nii_arr = nii_img.dataobj

    
    nii_arr = np.transpose(nii_arr, (0,2,1))
    nii_new = np.zeros(np.shape(nii_arr))

    for idx in range(np.shape(nii_arr)[-1]):
        nii_new[:,:,idx] = np.rot90(nii_arr[:,:,idx], k=3)

    if slice_num is None:
        slice_num = np.shape(nii_arr)[0]//2

    
    nii_bscan = nii_new[slice_num,:,:]
    m = np.min(nii_bscan)
    M = np.max(nii_bscan)
    nii_bscan = np.uint8((nii_bscan-m)/(M-m)*255)
    nii_bscan = np.rot90(nii_bscan, 3)

    nii_bscan_img = Image.fromarray(nii_bscan)
    nii_bscan_img.save(save_bscan_path, format='png')


def main():
    # subjects = [ i for i in range(10001,10501) ]
    arr = nib.load('/data/Nifti/In/Transformed/FOV_66/Mask_192/10001_mask_fov66_cropped.nii.gz')
    print(np.shape(arr))

    subjects = [10132]#, 10334]
    subjects.extend([i for i in range(10001, 10301, 50)])

    before_registered_dir = {'mask':'/data/Nifti/In/Before_Transformed/VolMask',
                             'octa':'/data/Nifti/In/Before_Transformed/OCTA',
                             'oct' :'/data/Nifti/In/Before_Transformed/OCT'}

    after_registered_dir = {'mask':'/data/Nifti/In/Transformed/VolMask',
                            'octa':'/data/Nifti/In/Transformed/OCTA',
                            'oct' :'/data/Nifti/In/Transformed/OCT'} # 10001_mask_translate_rigid.nii.gz

    bscan_dir = {'mask':'/data/Nifti/In/Transformed/Bscan/VolMask',
                 'octa':'/data/Nifti/In/Transformed/Bscan/OCTA',
                 'oct' :'/data/Nifti/In/Transformed/Bscan/OCT'} # 10001_mask_translate_rigid.nii.gz

    for subject in subjects:

        slice_num = 200//2 if subject<10301 else 304//2
        load_dir = '/data/Nifti/In/Transformed/FOV_66/Mask_192'
        cropped_path = os.path.join(load_dir, f'{subject}_mask_fov66_cropped.nii.gz')
        resized_path = os.path.join(load_dir, f'{subject}_mask_fov66_resized.nii.gz')


        make_bscan(load_nifti_path = cropped_path,
                   save_bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_reg_crop.png'),
                   slice_num = slice_num)

        make_bscan(load_nifti_path = resized_path,
                   save_bscan_path = os.path.join(bscan_dir['mask'], f'{subject}_reg_crop_resize.png'),
                   slice_num = slice_num)

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