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
        raise OSError("---> ERROR: The script in the shell was not correctly executed!")
    stt.solve_lis(image_dir, cat_division, stt_dir)
    return 0


def solve_lis_sample_rpi(cat_division, n_pic):
    if n_pic < 1 or n_pic > 50:
        raise ValueError("---> ERROR: --npic must be between 1 and 50")
    print("\n---> STT: Analyzing picture from Sample_images/RPi/img_{}.jpg "
          "using a catalog division of {}.\n".format(n_pic, cat_division))
    image_dir = "{}/Sample_images/RPi/img_{}.jpg".format(file_dir, n_pic)
    stt.solve_lis(image_dir, cat_division, stt_dir)
    return 0


def solve_lis_sample_stereo(cat_division, n_pic):
    if n_pic < 1 or n_pic > 10:
        raise ValueError("---> ERROR: --npic must be between 1 and 10")
    image_name = stereo_images(n_pic)
    print("\n---> STT: Analyzing picture from Sample_images/STEREO/{} "
          "using a catalog division of {}.\n".format(image_name, cat_division))
    image_dir = "{}/Sample_images/STEREO/{}".format(file_dir, image_name)
    stt.solve_lis(image_dir, cat_division, stt_dir, lis_type="stereo")
    return 0


def stereo_images(selector):
    stereo_images_list = ["20070130_080100_2bh1A_br01.fts",
                          "20070130_080100_s4h1A.fts",
                          "20080304_060901_2bh1A_br01.fts",
                          "20080304_060901_s4h1A.fts",
                          "20090417_052901_2bh1A_br01.fts",
                          "20090417_052901_s4h1A.fts",
                          "20090820_120901_2bh1A_br01.fts",
                          "20090820_120901_s4h1A.fts",
                          "20101220_192901_2bh1A_br01.fts",
                          "20101220_192901_s4h1A.fts"]
    image = stereo_images_list[selector - 1]
    return image
