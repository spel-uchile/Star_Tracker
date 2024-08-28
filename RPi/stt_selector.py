import os
import subprocess as sp
import stt_functions as stt

file_dir = os.path.abspath(os.path.dirname(__file__))
stt_dir = "{}/stt_data".format(file_dir)


def solve_lis_grab_img(cat_division, exposure_time_ms):
    exptime_micros = 1000 * exposure_time_ms
    image_dir = "{}/stt_img.jpg".format(stt_dir)
    print("\n---> STT: Taking picture with {} ms of exposure time.\n".format(exposure_time_ms))
    task = "libcamera-still -o {} -t 1 --width 1024 --height 1024 --shutter {}".format(image_dir, exptime_micros)
    process = sp.Popen(task, shell=True, stdout=sp.PIPE)
    process.wait()
    return_code = process.returncode
    if return_code != 0:
        raise OSError("The script in the shell was not correctly executed!")
    stt.solve_lis(image_dir, cat_division, stt_dir)
    return 0


def solve_lis_sample_rpi(cat_division, n_pic):
    print("\n---> STT: Analyzing picture from Sample_images/RPi/img_{}.jpg "
          "using a catalog division of {}.\n".format(n_pic, cat_division))
    image_dir = "{}/Sample_images/RPi/img_{}.jpg".format(file_dir, n_pic)
    stt.solve_lis(image_dir, cat_division, stt_dir)
    return 0


def solve_lis_sample_stereo(cat_division, n_pic):
    print(cat_division, n_pic)
    return 0
