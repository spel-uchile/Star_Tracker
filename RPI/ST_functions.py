# Imports.
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


# Define regular expressions that will be used in this script.
match_std_search = re.compile(r"sig=(-*\d\.\d+e...) Nr=(-*\d+)")
match_numbers_search = re.compile(r"a=(-*\d\.\d+e...) b=(-*\d\.\d+e...) c=(-*\d\.\d+e...) "
                                  r"d=(-*\d\.\d+e...) e=(-*\d\.\d+e...) f=(-*\d\.\d+e...)")


# Define directories and variable names.
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


# Define significant constant values to use in this script.
def st_constants():
    x_pix = 1024
    y_pix = 1024
    x_pix1 = int(x_pix/2)
    y_pix1 = int(y_pix/2)
    cmos2pix = 0.00270
    rpi_focal_mm = 3.04
    return x_pix1, y_pix1, cmos2pix, rpi_focal_mm


# Check the initial data entered to execute code in the terminal.
def review_init_data(sys_arg, len_arg):
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
def jpg2fits(pic_name, fits_name):
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


# Apply Source Extractor over an image and generates a catalog.
def apply_sextractor(dir_sext, dir_img_fits, fits_name, x_pix, y_pix, cmos2pix):
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


# Define RA/DEC list depending on the catalog division.
def generate_radec_list(cat_div):
    if cat_div == 10:
        ra_dec_list = [(ra, dec) for ra in range(0, 360, 10) for dec in range(-80, 90, 10)] + [(0, 90), (0, -90)]
    else:
        ra_dec_list = [(ra, dec) for ra in range(0, 360, 5) for dec in range(-85, 90, 5)] + [(0, 90), (0, -90)]
    return ra_dec_list


# Define and set the 'match' string before calling it in the shell.
def set_match_str(ra, dec, dir_stars, dir_proj_cat2, param):
    ra_dec_str = str(ra) + '_DEC_' + str(dec)
    match_str = 'match ' + dir_stars + ' 0 1 2 ' + dir_proj_cat2 + ra_dec_str + ' 0 1 2 ' + param
    return match_str


# Variables for use in 'set_match_str' inside 'call_match'.
DIR_stars = names_and_dir()[2]
DIR_proj_cat2 = names_and_dir()[6]
param1 = 'trirad=0.002 nobj=15 max_iter=1 matchrad=1 scale=1'


# Call 'Match' with RA/DEC list in the shell.
def call_match(ra_dec_list):
    ra, dec = ra_dec_list
    match = set_match_str(ra, dec, DIR_stars, DIR_proj_cat2, param1)
    status, result = commands.getstatusoutput(match)
    return status, result


# Apply 'call_match' multiprocessing depending on numbers of cores.
def map_match_and_radec_list_multiprocess(ra_dec_list):
    n_cores = multiprocessing.cpu_count()
    if n_cores == 1:
        first_match_results = map(call_match, ra_dec_list)
    else:
        pool = multiprocessing.Pool(n_cores)
        first_match_results = pool.map(call_match, ra_dec_list)
    return first_match_results


# Select RA/DEC values in which a successful match was obtained, and generate a 'match' table.
def get_table_with_matchs(ra_dec_list, first_match_results):
    match_table = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))
    for i, (status, result) in enumerate(first_match_results):
        if status == 0:
            ra, dec = ra_dec_list[i]
            regexp_result = match_std_search.findall(result)[0]
            sig = float(regexp_result[0])
            nr = int(regexp_result[1])
            match_table.add_row([str(ra), str(dec), sig, nr])
    if len(match_table) == 0:
        print '- Can not find any match between picture and catalog!'
        raise ValueError('There is NO match ...')
    else:
        match_table.sort('Nr')
        match_table.reverse()
    return match_table


# Select three (3) 'match' candidates from 'first match table'.
def get_match_candidates(match_table):
    len_table = len(match_table)
    if len_table == 1:
        match_candidates = match_table
    elif len_table == 2:
        match_table.sort('sig')
        match_candidates = match_table
    else:
        short_match_table = match_table[0:3]
        short_match_table.sort('sig')
        match_candidates = short_match_table
    return match_candidates


# With a list of 'match candidates', recall match to obtain the transformation data.
def get_first_match_data(candidates, try_n):
    cand = candidates[try_n]
    result = call_match([int(cand[0]), int(cand[1])])[1]
    regexp_result = match_numbers_search.findall(result)[0]
    return regexp_result


# Apply the 'match' transformation between picture and projected catalog.
# This is: center of picture (pix) ==> point in the projected catalog (pix).
# This function CAN BE USEFUL!
# def apply_match_trans(data):
#     match_a = float(data[0])
#     match_b = float(data[1])
#     match_c = float(data[2])
#     match_d = float(data[3])
#     match_e = float(data[4])
#     match_f = float(data[5])
#     match_translation = np.array([match_a, match_d])
#     match_rotation = np.array([(match_b, match_c), (match_e, match_f)])
#     match_x_pix = np.array([0, 0])
#     match_x_sky = match_translation + np.dot(match_rotation, match_x_pix)
#     print ' --- match sky --- '
#     print match_x_sky
#     match_ra_pix, match_dec_pix = match_x_sky[0], match_x_sky[1]
#     match_roll_rad = np.arctan2(match_c, match_b)
#     match_roll_deg = np.rad2deg(match_roll_rad)
#     return match_ra_pix, match_dec_pix, match_roll_deg
def apply_match_trans(data):
    match_a = float(data[0])
    match_b = float(data[1])
    match_c = float(data[2])
    match_d = float(data[3])
    match_ra_pix, match_dec_pix = match_a, match_d
    match_roll_rad = np.arctan2(match_c, match_b)
    match_roll_deg = np.rad2deg(match_roll_rad)
    return match_ra_pix, match_dec_pix, match_roll_deg


# It deproject the (0, 0) point of the camera. This is: any pixel ==> sky coordinates.
def deproject(focal_len, ra_match_pix, dec_match_pix, ra_catalog, dec_catalog):
    xi = ra_match_pix/float(focal_len)
    eta = dec_match_pix/float(focal_len)
    dec_catalog_rad = np.deg2rad(dec_catalog)
    arg1 = np.cos(dec_catalog_rad) - eta*np.sin(dec_catalog_rad)
    arg2 = np.arctan(xi/arg1)
    arg3 = np.sin(arg2)
    arg4 = eta*np.cos(dec_catalog_rad) + np.sin(dec_catalog_rad)
    alpha = ra_catalog + np.rad2deg(arg2)
    delta = np.rad2deg(np.arctan((arg3*arg4)/xi))
    return alpha, delta


# Search in the normal catalog for objects with which a 'match' was done, and create a table with catalog coincidences.
def search_catalog_objects(dir_normal_cat, ra_catalog, dec_catalog):
    new_cat_name = dir_normal_cat + 'cat_RA_' + str(int(ra_catalog)) + '_DEC_' + str(int(dec_catalog))
    new_cat = ascii.read(new_cat_name)
    noproj_matched_b1 = ascii.read('./matched.mtB')
    noproj_matched_b2 = ascii.read('./matched.unB')
    noproj_counter = min(noproj_matched_b1[0][0], noproj_matched_b2[0][0])
    noproj_table = Table([[], [], []])
    for i in range(len(noproj_matched_b1)):
        noproj_counter2 = noproj_matched_b1[i][0] - noproj_counter
        noproj_table.add_row([new_cat[noproj_counter2][0], new_cat[noproj_counter2][1], new_cat[noproj_counter2][2]])
    return noproj_table
