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
    dir_first_match_output = dir_img_fits + 'new_cat'
    dir_sext = './sextractor'
    dir_proj_cat1 = './Catalog/Projected/'
    dir_proj_cat2 = dir_proj_cat1 + 'cat_RA_'
    dir_normal_cat = './Catalog/Normal/'
    fits_name = 'img_fits.fits'
    return dir_this, dir_img_fits, dir_stars, dir_first_match_output, dir_sext, dir_proj_cat1, \
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
    sextractor_stars = 40
    sext2 = sext1[0:sextractor_stars]
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
param2 = 'trirad=0.002 nobj=20 max_iter=3 matchrad=1 scale=1'


# Call 'Match' with RA/DEC list in the shell.
def call_match_list(ra_dec_list):
    ra, dec = ra_dec_list
    match = set_match_str(ra, dec, DIR_stars, DIR_proj_cat2, param1)
    status, result = commands.getstatusoutput(match)
    return status, result


# Call 'Match' one time, in further 'match' iterations.
def call_match_once(dir_stars, new_proj_cat):
    match_str = 'match ' + dir_stars + ' 0 1 2 ' + new_proj_cat + ' 0 1 2 ' + param2
    status, result = commands.getstatusoutput(match_str)
    regexp_result_numbers = match_numbers_search.findall(result)[0]
    regexp_result_std = match_std_search.findall(result)[0]
    return regexp_result_numbers, regexp_result_std


# Apply 'call_match' multiprocessing depending on numbers of cores.
def map_match_and_radec_list_multiprocess(ra_dec_list):
    n_cores = multiprocessing.cpu_count()
    if n_cores == 1:
        first_match_results = map(call_match_list, ra_dec_list)
    else:
        pool = multiprocessing.Pool(n_cores)
        first_match_results = pool.map(call_match_list, ra_dec_list)
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
        print '- After search in the whole catalog, I can not find any match between picture and catalog!'
        raise ValueError('There is no match ...')
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
    result = call_match_list([int(cand[0]), int(cand[1])])[1]
    regexp_result_numbers = match_numbers_search.findall(result)[0]
    regexp_result_std = match_std_search.findall(result)[0]
    return regexp_result_numbers, regexp_result_std


# Apply the 'match' transformation between picture and projected catalog.
# This is: center of picture (pix) ==> point in the projected catalog (pix).
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


# With a list of 'matched' stars, project all in a tangent plane.
def sky2plane(star_list, ra_project_point, dec_project_point, focal_len):
    cat_proj = Table([[], [], []])
    stars_len = len(star_list)
    for index in range(stars_len):
        alpha_deg = star_list[index][0]
        delta_deg = star_list[index][1]
        mag = star_list[index][2]
        alpha_rad = np.deg2rad(alpha_deg)
        delta_rad = np.deg2rad(delta_deg)
        alpha_0_rad = np.deg2rad(ra_project_point)
        delta_0_rad = np.deg2rad(dec_project_point)
        xi_up = np.cos(delta_rad)*np.sin(alpha_rad - alpha_0_rad)
        xi_down = np.sin(delta_0_rad)*np.sin(delta_rad) \
            + np.cos(delta_0_rad)*np.cos(delta_rad)*np.cos(alpha_rad - alpha_0_rad)
        xi = xi_up/xi_down
        eta_up = np.cos(delta_0_rad)*np.sin(delta_rad) \
            - np.sin(delta_0_rad)*np.cos(delta_rad)*np.cos(alpha_rad - alpha_0_rad)
        eta_down = xi_down
        eta = eta_up/eta_down
        xi_mm = xi*focal_len
        eta_mm = eta*focal_len
        cat_proj.add_row([xi_mm, eta_mm, mag])
    cat_name = 'new_cat'
    ascii.write(cat_proj, cat_name, delimiter=' ', format='no_header', overwrite=True,
                formats={'X': '% 15.5f', 'Y': '% 15.5f', 'Z': '% 15.2f'}, names=['X', 'Y', 'Z'])
    return 0


# Set the RA and Roll coordinates in a standard way (like STEREO way!).
def normalize_coord(ra, roll):
    if ra > 180.0:
        ra_out = ra - 360.0
    else:
        ra_out = ra
    if roll < 0.0:
        roll_out = roll + 180.0
    else:
        roll_out = roll - 180.0
    return ra_out, roll_out


# Save attitude solution to a file.
def save_data(pic_name1, ra, dec, roll, sig, nr):
    att_file = open('attitude_data.txt', 'a')
    pic_name2 = pic_name1.split('/')[-1]
    to_write = pic_name2 + ' ' + str(ra) + ' ' + str(dec) + ' ' + str(roll) + ' ' + str(sig) + ' ' + str(nr) + '\n'
    att_file.write(to_write)
