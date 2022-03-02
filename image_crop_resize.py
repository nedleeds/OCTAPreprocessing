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
    ret, thr = cv2.threshold(imgray, 10, 255, cv2.THRESH_BINARY)

    detector = cv2.SimpleBlobDetector()
    keypoints = detector.detect(Image.fromarray(np.uint8(thr)).convert("RGB"))
    im_with_keypoints = cv2.drawKeypoints(imgray, keypoints, np.array([]), (0,0,255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    np.min(thr)

    # contours, hierarchy = cv2.findContours(thr, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # img_contours = np.zeros(imgray.shape)
    # cv2.drawContours(img_contours, contours, -1, (0,255,0), 3)
    # cv2.imshow(img_contours)

def main():
    subjects = [ i for i in range(10001,10501) ]

    for subject in subjects:
        if subject < 10301:
            before_crop_dir = '/data/dataset/OCTA-500/OCTA_6M/Projection Maps/OCTA(ILM_OPL)'
            after_crop_dir = '/data/dataset/OG/OCTA_Enface'
            crop_area_dir = '/data/dataset/OG/OCTA_Enface_with_crop_area'
            os.makedirs(crop_area_dir, exist_ok=True)

            make_enface(load_nifti_path=f'/data/Nifti/In/FOV_66/OCTA_srl/{subject}.nii.gz',
                        save_enface_path=f'/home/dhl/Project/OCTPreprocessing/enface/{subject}.png')

            # image_crop(load_image_path = os.path.join(before_crop_dir, f'{subject}.bmp'),
            #            save_image_path = os.path.join(after_crop_dir, f'{subject}.png'),
            #            crop_area_path = os.path.join(crop_area_dir,f'{subject}.png'),
            #            cropped_size = (200, 200),
            #            is_display = False)

            # image_resize(load_image_path = os.path.join(after_crop_dir, f'{subject}.png'), 
            #              save_image_path = os.path.join(after_crop_dir, f'{subject}.png'),
            #              resized_size = (192, 192), 
            #              is_display = False)

        else:
            before_resize_dir = '/data/dataset/OCTA-500/OCTA_3M/Projection Maps/OCTA(ILM_OPL)'
            after_resize_dir = '/data/dataset/OCTA_Enface'
            image_resize(load_image_path = os.path.join(before_resize_dir, f'{subject}.bmp'), 
                         save_image_path = os.path.join(after_resize_dir, f'{subject}.png'),
                         resized_size = (192, 192), 
                         is_display = False)

        print(f'{subject} has been saved.')

main()