from enum import Flag
import os
import cv2
import numpy as np
import nibabel as nib
import matplotlib
import matplotlib.pyplot as plt
from PIL import Image

def check_normalization(load_path, save_dir, subject):
    if 'nii' in load_path:
        arr = np.asarray(nib.load(load_path).dataobj)
    else:
        arr = np.rot90(np.asarray(Image.open(load_path)))
        
    print(f'mean : {arr.mean()}', end=' -> ')
    #### Get Nifti - OG, Min/Max Normalized, Mean Normalized. ####
    m = np.min(arr)
    M = np.max(arr)
    arr_min_max = np.uint8((arr - m) / (M-m) * 255)
    # arr_mean_convert = (arr_min_max / np.mean(arr_min_max)) * (80)
    arr_clip_up = np.zeros(np.shape(arr_min_max))
    arr_clip_up_low = np.zeros(np.shape(arr_min_max))
    
    lower = np.percentile(arr[np.where(arr > 0)], 2)
    upper = np.percentile(arr[np.where(arr > 0)], 99.94)
    arr_clip_up[arr <= upper] = arr[arr <= upper]
    arr_clip_up_low[(lower <= arr) & (arr <= upper)] = arr[(lower <= arr) & (arr <= upper)]
    

    arr_clip_up = np.uint8((arr_clip_up - arr_clip_up.min()) / (arr_clip_up.max()-arr_clip_up.min())*255)
    arr_clip_up_low = np.uint8((arr_clip_up_low - arr_clip_up_low.min()) / (arr_clip_up_low.max()-arr_clip_up_low.min())*255)

    # contrast limit가 2이고 title의 size는 8X8
    clahe = cv2.createCLAHE(clipLimit=4, tileGridSize=(4,4))
    arr_clip_up_low = clahe.apply(arr_clip_up_low)
    # dst = cv2.equalizeHist(arr_clip_up_low)

    #### Convert numpy array to PIL image & Save PIL image ####
    pil_img_og = Image.fromarray(np.rot90(np.uint8(arr)))
    pil_img_min_max = Image.fromarray(np.rot90(np.uint8(arr_min_max)))
    pil_img_clip_up = Image.fromarray(np.rot90(np.uint8(arr_clip_up)))
    pil_img_clip_up_low = Image.fromarray(np.rot90(np.uint8(arr_clip_up_low)))
    print(f'mean : {arr_clip_up_low.mean()}')

    #### Save 
    pil_img_og.save(os.path.join(save_dir, f'{subject}_og.png'), "PNG")
    pil_img_min_max.save(os.path.join(save_dir, f'{subject}_min_max.png'), "PNG")
    pil_img_clip_up.save(os.path.join(save_dir, f'{subject}_clip_up.png'), "PNG")
    pil_img_clip_up_low.save(os.path.join(save_dir, f'{subject}_clip_up_low.png'), "PNG")

    font = {'size' : 25}

    matplotlib.rc('font', **font)

    fig, axes = plt.subplots(2, 4, figsize=(44, 20), layout='constrained')

    hist_og, bin_edges_og = np.histogram(arr[np.where(arr > 0)])
    hist_min_max, bin_edges_min_max = np.histogram(arr_min_max[np.where(arr_min_max > 0)])
    hist_clip_up, bin_edges_clip_up = np.histogram(arr_clip_up[np.where(arr_clip_up > 0)])
    hist_clip_up_low, bin_edges_clip_up_low = np.histogram(arr_clip_up_low[np.where(arr_clip_up_low > 0)])

    axes[0,0].plot(bin_edges_og[0:-1], hist_og, label=f'intensity mean : {np.round(np.mean(arr),3)}')
    i1 = axes[0,1].imshow(pil_img_og, cmap = 'gray')
    axes[0,2].plot(bin_edges_min_max[0:-1], hist_min_max, label=f'intensity mean : {np.round(np.mean(arr_min_max),3)}')
    i2 = axes[0,3].imshow(pil_img_min_max, cmap = 'gray')
    axes[1,0].plot(bin_edges_clip_up[0:-1], hist_clip_up, label=f'intensity mean : {np.round(np.mean(arr_clip_up),3)}')
    i3 = axes[1,1].imshow(pil_img_clip_up, cmap = 'gray')
    axes[1,2].plot(bin_edges_clip_up_low[0:-1], hist_clip_up_low, label=f'intensity mean : {np.round(np.mean(arr_clip_up_low),3)}')
    i4 = axes[1,3].imshow(pil_img_clip_up_low, cmap = 'gray')

    axes[0,0].set_title(f"IEEE-OCTA500")
    axes[0,0].set_xlabel('grayscale value')
    axes[0,0].set_ylabel('pixel count')
    axes[0,0].legend(prop={'size':25}, loc='best')
    axes[0,1].set_title(f"{subject} En-Face")

    axes[0,2].set_title(f"Min/Max x 255")
    axes[0,2].set_xlabel('grayscale value')
    axes[0,2].set_ylabel('pixel count')
    axes[0,2].legend(prop={'size':25}, loc='best')
    axes[0,3].set_title(f"{subject} En-Face")

    axes[1,0].set_title(f"Clipping(upper:0.01%) + Min/Max x 255")
    axes[1,0].set_xlabel('grayscale value')
    axes[1,0].set_ylabel('pixel count')
    axes[1,0].legend(prop={'size':25}, loc='best')
    axes[1,1].set_title(f"{subject} En-Face")

    axes[1,2].set_title(f"Clipping(upper:0.01%, lower:1%) + Min/Max x 255")
    axes[1,2].set_xlabel('grayscale value')
    axes[1,2].set_ylabel('pixel count')
    axes[1,2].legend(prop={'size':25}, loc='best')
    axes[1,3].set_title(f"{subject} En-Face")

    # plt.show()
    fig.colorbar(i1, ax = axes[0,1])
    fig.colorbar(i2, ax = axes[0,3])
    fig.colorbar(i3, ax = axes[1,1])
    fig.colorbar(i4, ax = axes[1,3])
    plt.savefig(fname = os.path.join(save_dir, f'{subject}_histogram.png'))
    plt.close('all')

    print(f"{subject} has been checked.")

def main():
    for idx in range(10055, 10301):
        load_enface = f'/data/dataset/OG/{idx}.png'
        check_normalization(load_path = load_enface,
                            save_dir = '/data/Nifti/In/Transformed/Normalized/Histogram/0311',
                            subject = idx)


main()

