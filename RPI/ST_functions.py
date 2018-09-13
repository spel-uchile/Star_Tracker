# Imports.
import time
import os
import re
import subprocess
import multiprocessing
import commands
import numpy as np
from PIL import Image
from astropy.io import fits, ascii
from astropy.table import Table
import platform


# Define directories and names.
def names_and_dir():
    dir_this = os.path.dirname(os.path.abspath(__file__)) + '/'
    dir_img_fits = dir_this
    dir_stars = dir_img_fits + 'sext'
    dir_first_match = dir_img_fits + 'new_cat'
    dir_sext = './sextractor'
    dir_proj_cat1 = './Catalog/Projected/'
    dir_proj_cat2 = dir_proj_cat1 + 'cat_RA_'
    dir_normal_cat = './Catalog/Normal/'
    fits_name = 'img_fits.fits'
    return dir_this, dir_img_fits, dir_stars, dir_first_match, dir_sext, dir_proj_cat1,\
           dir_proj_cat2, dir_normal_cat, fits_name


# Define significant constant values.
def st_constants():
    x_pix = 1024
    y_pix = 1024
    x_pix1 = int(x_pix/2)
    y_pix1 = int(y_pix/2)
    cmos_to_pix = 0.00270
    return x_pix1, y_pix1, cmos_to_pix


# Check the initial data entered to execute code in the terminal.
def rev_initial_data(sys_arg, len_arg):
    if len_arg == 1:
        print '- Too few arguments...'
        print '- Add the full directory of the image.'
        raise ValueError('Not enough data...')
    elif len_arg == 2:
        pic_name = sys_arg[1]
        catalog_division = 10
        print '- Using default catalog division (10 degrees).'
    elif len_arg == 3:
        pic_name = sys_arg[2]
        if int(sys_arg[1]) == 5:
            catalog_division = 5
            print '- Catalog division: 5 degrees.'
        else:
            print '- Unknown catalog division.'
            raise ValueError('Invalid data...')
    elif len_arg > 3:
        print '- Too many arguments.'
        raise ValueError('Invalid data...')
    else:
        print '- Unknown error.'
        raise ValueError('Invalid data...')
    return pic_name, catalog_division


# Generate '.fits' from '.jpg' image.
def generate_fits(pic_name, fits_name):
    image = Image.open(pic_name)
    imagebw = image.convert('L')
    xsize, ysize = imagebw.size
    fits1 = imagebw.getdata()
    if platform.machine().endswith('64'):
        fits2 = np.array(fits1, dtype=np.int32)
    else:
        fits2 = np.array(fits1)
    fits3 = fits2.reshape(ysize, xsize)
    fits4 = np.flipud(fits3)
    fits5 = fits.PrimaryHDU(data=fits4)
    fits5.writeto(fits_name, overwrite=True)
    return 0


# Apply Source Extractor over an image.
def apply_sext(dir_sext, dir_img_fits, fits_name, x_pix, y_pix, cmos2pix):
    os.chdir(dir_sext)
    imdir = dir_img_fits + fits_name
    sext_task = 'sextractor ' + imdir
    subprocess.check_output(sext_task, shell=True)
    sext1 = ascii.read('./test.cat', format='sextractor')
    sext1.sort(['MAG_ISO'])
    sext2 = sext1[0:40]
    os.chdir(dir_img_fits)
    sext_x = sext2['X_IMAGE']
    sext_y = sext2['Y_IMAGE']
    sext_mag = sext2['MAG_ISO']
    sext_x1 = (sext_x - x_pix)*cmos2pix
    sext_y1 = (sext_y - y_pix)*cmos2pix
    sext_fname = 'sext'
    ascii.write([sext_x1, sext_y1, sext_mag], sext_fname, delimiter=' ', format='no_header', overwrite=True,
                formats={'X': '% 15.10f', 'Y': '% 15.10f', 'Z': '% 15.10f'}, names=['X', 'Y', 'Z'])
    return 0


# Execute 'match' in the shell.
def call_match(ra_dec_list, DIR_stars, dir_proj_cat2, param1):
    ra, dec = ra_dec_list
    path_catalog1 = str(ra) + '_DEC_' + str(dec)
    path_catalog2 = dir_proj_cat2 + path_catalog1
    # Do Match.
    Match = 'match ' + DIR_stars + ' 0 1 2 ' + path_catalog2 + ' 0 1 2 ' + param1
    status, result = commands.getstatusoutput(Match)
    return status, result