import os
import stt_functions as stt


def solve_lis_grab_img(exposure_time, cat_division):
    print(exposure_time, cat_division)
    return 0


def solve_lis_sample_rpi(cat_division, n_pic):
    print(cat_division, n_pic)
    file_dir = os.path.abspath(os.path.dirname(__file__))
    image_dir = "{}/Sample_images/RPi/img_{}.jpg".format(file_dir, n_pic)
    stt_dir = "{}/stt_data".format(file_dir)
    stt.solve_lis(image_dir, cat_division, stt_dir)
    return 0


def solve_lis_sample_stereo(cat_division, n_pic):
    print(cat_division, n_pic)
    return 0

