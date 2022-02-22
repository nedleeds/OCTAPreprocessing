import os
import numpy as np
import nibabel as nib
class Resize():
    def __init__(self) -> None:
        self.load_dir = ''
        self.save_dir = ''
        self.subeject_list = []
        self.cropped_size = None
        self.original_size = None
        self.resized_size = None

    def cropping(self, before_size, after_size):
        self.is_cropping = True
        self.cropped_size = after_size
        self.original_size = before_size

    def set_dir(self, load_dir, save_dir):
        assert (load_dir is not None) and (save_dir is not None), \
                'You need to set load and save directory.' 

        self.load_dir = load_dir
        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)

    def set_subject_list(self, subject_list):
        self.subeject_list = subject_list

    def load_nifti(self, load_path):
        assert load_path is not None, 'You need to set load_path for load nifti file.'
        nifti_img = nib.load(load_path)
        yield nifti_img.dataobj, nifti_img.header

    def show_nifti_header(self, nifti_header):
        for k in nifti_header:
            print(f'{k} : {nifti_header[k]}')

    def resizing(self, before_size, after_size):
        self.original_size = before_size
        self.resized_size = after_size

        for subject in self.subeject_list:
            nifti_path = os.path.join(self.load_dir, f'{subject}.nii.gz')
            
            # self.resize_nifti(nifti_data = nii_data, 
            #                   current_size = nii_data.shape, 
            #                   resized_size = self.resized_nifti)

    def cropping(self, before_size, after_size):
        self.original_size = before_size
        self.cropped_size = after_size

        for subject in self.subeject_list:
            load_path = os.path.join(self.load_dir, f'{subject}.nii.gz')
            save_path = os.path.join(self.save_dir, f'{subject}_cropped.nii.gz')

            nii_data, nii_info = next(self.load_nifti(load_path=load_path))
            assert self.original_size == nii_data.shape, 'original size should be same with loaded nifti size.'
            # self.show_nifti_header(nifti_header=nii_info)
                
            w_o, h_o, d_o = self.original_size
            w_c, h_c, d_c = self.cropped_size
            w_diff, h_diff, d_diff = (w_o-w_c)//2, (h_o-h_c)//2, (d_o-d_c)//2
            
            before_nii = np.transpose(nii_data, (0,2,1))
            cropped_nii = np.zeros((w_c, d_c, h_c))

            for idx in range(h_o):
                cropped_nii[:, :, idx] = before_nii[w_diff:w_o-w_diff, d_diff:d_o-d_diff, idx]
            
            cropped_nii = np.transpose(cropped_nii, (0, 2, 1))
            w_c, h_c, d_c = cropped_nii.shape

            print(f'before cropping - width, height, depth : {w_o}, {h_o}, {d_o}')
            print(f'after  cropping - width, height, depth : {w_c}, {h_c}, {d_c}')

            self.save_nifti(nifti_data = cropped_nii, 
                            before_info = nii_info, 
                            after_info = self.get_FOV33_info(nii_size=self.cropped_size),
                            save_path = save_path)

    def get_FOV33_info(self, nii_size):
        scale = 19*3
        fov33_size = (3, 2, 3)  # fov66_size = (6, 6, 2)
        resolution = [(f*scale) for f in fov33_size]
        spacing = [(r/v) for r,v in zip(resolution, nii_size)]
        origin = [-r//2 for r in resolution]

        new_info = {'pixel' : self.cropped_size,
                    'origin' : origin,
                    'spacing': spacing}

        return new_info


    def save_nifti(self, nifti_data, before_info, after_info, save_path):
        w_pix, h_pix, d_pix = after_info['pixel']
        w_spacing, h_spacing, d_spacing = after_info['spacing']
        w_origin, h_origin, d_origin = after_info['origin']

        nifti_info_new =before_info
        nifti_info_new['dim'] = [3, w_pix, h_pix, d_pix, 1, 1, 1, 1]
        nifti_info_new['xyzt_units'] = 0
        nifti_info_new['pixdim'] = [1., w_spacing, h_spacing, d_spacing, 1., 1., 1., 1.]
        nifti_info_new['qoffset_x'] = -w_origin
        nifti_info_new['qoffset_y'] = -h_origin
        nifti_info_new['qoffset_z'] = d_origin
        nifti_info_new['srow_x'] = [-w_spacing, 0, 0, -w_origin]
        nifti_info_new['srow_y'] = [0, -h_spacing, 0, -h_origin]
        nifti_info_new['srow_z'] = [0, 0,  d_spacing,  d_origin]

        nifti_new_img = nib.Nifti1Image(nifti_data, nifti_info_new.get_best_affine())
        nib.save(nifti_new_img, save_path)
        print(f'nifti saved at {save_path}')

    # def resize_nifti(self, nifti_data):



def main():
    load_dir = {'FOV66' : ['/data/Nifti/In/FOV_66/OCT', '/data/Nifti/In/FOV_66/OCTA'],
                'FOV33' : ['/data/Nifti/In/FOV_33/OCT', '/data/Nifti/In/FOV_33/OCTA']}

    resized_dir = {'FOV66' : ['/data/Nifti/In/FOV_66/OCT_Resized', '/data/Nifti/In/FOV_66/OCTA_Resized'],
                   'FOV33' : ['/data/Nifti/In/FOV_33/OCT_Resized', '/data/Nifti/In/FOV_33/OCTA_Resized']}

    subject_list = {'FOV66' : [subject for subject in range(10001, 10301)],
                    'FOV33' : [subject for subject in range(10301, 10501)]}

    original_size = {'FOV66' : (400, 640, 400),
                     'FOV33' : (304, 640, 304)}

    croped_size = (262, 640, 262)
    resized_size = (256, 640, 256)

    resizer = Resize()
    for nii_dir, resize_dir in zip(load_dir['FOV66'], resized_dir['FOV66']):
        resizer.set_dir(load_dir=nii_dir, save_dir=resize_dir)
        resizer.set_subject_list(subject_list['FOV66'])
        resizer.cropping(before_size = original_size['FOV66'], after_size = croped_size)
        # resizer.resizing(before_size = original_size['FOV66'], after_size = resized_size)
        


main()