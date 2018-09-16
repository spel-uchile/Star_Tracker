# Imports.
import time
import os
import re
import subprocess
import commands
import numpy as np
import multiprocessing
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
    return dir_this, dir_img_fits, dir_stars, dir_first_match, dir_sext, dir_proj_cat1, \
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


# Define RA/DEC list depending on catalog division.
def generate_ra_dec_list(cat_div):
    if cat_div == 10:
        ra_dec_list = [(ra, dec) for ra in range(0, 360, 10) for dec in range(-80, 90, 10)] + [(0, 90), (0, -90)]
    else:
        ra_dec_list = [(ra, dec) for ra in range(0, 360, 5) for dec in range(-85, 90, 5)] + [(0, 90), (0, -90)]
    return ra_dec_list


# Define and set 'match' before calling it in the shell.
def set_match(ra_dec_str, dir_stars, dir_proj_cat2, param):
    match_str = 'match ' + dir_stars + ' 0 1 2 ' + dir_proj_cat2 + ra_dec_str + ' 0 1 2 ' + param
    return match_str


# Variables for use in 'set_call_match' inside 'call_match'.
DIR_stars = names_and_dir()[2]
DIR_proj_cat2 = names_and_dir()[6]
param1 = 'trirad=0.002 nobj=15 max_iter=1 matchrad=1 scale=1'


# Call 'Match' with RA/DEC list in the shell.
def call_match(ra_dec_list):
    ra, dec = ra_dec_list
    ra_dec_str = str(ra) + '_DEC_' + str(dec)
    match = set_match(ra_dec_str, DIR_stars, DIR_proj_cat2, param1)
    status, result = commands.getstatusoutput(match)
    return status, result


# Apply multiprocessing depending on numbers of cores. Then, apply 'call_match'.
def apply_map_multiprocess(ra_dec_list):
    n_cores = multiprocessing.cpu_count()
    if n_cores == 1:
        first_match_results = map(call_match, ra_dec_list)
    else:
        pool = multiprocessing.Pool(n_cores)
        first_match_results = pool.map(call_match, ra_dec_list)
    return first_match_results


# Select RA/DEC values in which a correct match was obtained, and generate a 'match' table.
def generate_matchs_table(ra_dec_list, first_match_results):
    match_table = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))
    match_search = re.compile(r"sig=(-*\d\.\d+e...) Nr=(-*\d+)")
    for i, (status, result) in enumerate(first_match_results):
        if status == 0:
            ra, dec = ra_dec_list[i]
            reg_result = match_search.findall(result)
            sig = float(reg_result[0][0])
            nr = int(reg_result[0][1])
            match_table.add_row([str(ra), str(dec), sig, nr])
    if len(match_table) == 0:
        print 'Can not find any match between picture and catalog!'
        raise ValueError('There is NO match...')
    else:
        match_table.sort('Nr')
        match_table.reverse()
    return match_table
