import multiprocessing
import numpy as np
import os
import platform
import re
import subprocess as sp
import time
from astropy.io import fits, ascii
from astropy.table import Table
from itertools import repeat
from PIL import Image

# NAMES
SEXTRACTOR_STR = "source-extractor"
# DIRECTORIES
DIR_STARS = "sext"
DIR_PROJ_CAT_RPI = "/home/samuel/github/Star_Tracker/RPi/Catalog/RPi/Projected"
DIR_PROJ_CAT_STEREO = "/home/samuel/github/Star_Tracker/RPi/Catalog/STEREO/Projected"
DIR_NORMAL_CAT_RPI = "/home/samuel/github/Star_Tracker/RPi/Catalog/RPi/Normal"
DIR_NORMAL_CAT_STEREO = "/home/samuel/github/Star_Tracker/RPi/Catalog/STEREO/Normal"
NEW_PROJ_CAT = 'new_cat'
# ALGORITHM PARAMETERS
SEXTRACTOR_MAX_STARS = 40
X_PIX = 512
Y_PIX = 512
PIX2MM_RPI = 0.002695
PIX2MM_STEREO = 0.027021
LIS_MAX_ITER = 3
FOCAL_LEN_MM_RPI = 3.04
FOCAL_LEN_MM_STEREO = 78.46
# MATCH PARAMETERS
PARAM1 = "trirad=0.002 nobj=15 max_iter=1 matchrad=0.1 scale=1"
PARAM2 = "trirad=0.002 nobj=20 max_iter=5 matchrad=0.01 scale=1"
# REGULAR EXPRESSIONS
MATCH_STD = re.compile(r"sig=(-*\d\.\d+e...) Nr=(-*\d+) Nm=(-*\d+) sx=(-*\d\.\d+e...) sy=(-*\d\.\d+e...)")
MATCH_NUMBERS = re.compile(r"a=(-*\d\.\d+e...) b=(-*\d\.\d+e...) c=(-*\d\.\d+e...) "
                           r"d=(-*\d\.\d+e...) e=(-*\d\.\d+e...) f=(-*\d\.\d+e...)")


def jpg2fits(full_dir_img, fits_name_of_image):
    """
    Generate .fits from .jpg image.
    """
    image = Image.open(full_dir_img)
    image_bw = image.convert('L')
    x_size, y_size = image_bw.size
    fits1 = image_bw.getdata()
    if platform.machine().endswith('64'):
        fits2 = np.array(fits1, dtype=np.int32)
    else:
        fits2 = np.array(fits1)
    fits3 = fits2.reshape(y_size, x_size)
    fits4 = np.flipud(fits3)
    fits5 = fits.PrimaryHDU(data=fits4)
    fits5.writeto(fits_name_of_image, overwrite=True)
    return 0


def apply_sextractor(img_fits_name, stt_data_dir, lis_type="rpi"):
    """
    Apply Source Extractor over an image and generates a catalog.
    """
    if lis_type == "rpi":
        pix2mm = PIX2MM_RPI
    elif lis_type == "stereo":
        pix2mm = PIX2MM_STEREO
    else:
        raise NameError("ERROR: See function apply_sextractor")
    os.chdir(stt_data_dir)
    sext_task = "{} {}".format(SEXTRACTOR_STR, img_fits_name)
    sp.check_output(sext_task, shell=True)
    sext1 = ascii.read('./test.cat', format='sextractor')
    sext1.sort(['MAG_ISO'])
    sext2 = sext1[0:SEXTRACTOR_MAX_STARS]
    sext_x_pix = sext2['X_IMAGE']
    sext_y_pix = sext2['Y_IMAGE']
    sext_mag = sext2['MAG_ISO']
    sext_x_mm = (sext_x_pix - X_PIX) * pix2mm
    sext_y_mm = (sext_y_pix - Y_PIX) * pix2mm
    sext_filename = 'sext'
    ascii.write([sext_x_mm, sext_y_mm, sext_mag], sext_filename, delimiter=' ', format='no_header', overwrite=True,
                formats={'X': '% 15.10f', 'Y': '% 15.10f', 'Z': '% 15.10f'}, names=['X', 'Y', 'Z'])
    return sext_x_pix, sext_y_pix, sext_x_mm, sext_y_mm


def get_catalog_center_points(x_center, y_center, distance, lis_type="rpi"):
    """
    Get the center points for different catalogs segments, for a given distance and starting point.
    It considers declination of center site.
    """
    if lis_type == "rpi":
        catalog_center_list = list()
        for jj1 in range(y_center, 90, distance):
            aux1 = (1 / np.cos(np.deg2rad(jj1)))
            distance_ra1 = int(round(distance * aux1))
            for ii1 in range(x_center, 360, distance_ra1):
                 catalog_center_list.append([ii1, jj1])
        for jj2 in range(y_center - distance, -90, -distance):
            aux2 = (1 / np.cos(np.deg2rad(jj2)))
            distance_ra2 = int(round(distance * aux2))
            for ii2 in range(x_center, 360, distance_ra2):
                catalog_center_list.append([ii2, jj2])
        catalog_center_list = catalog_center_list + [[0, 90], [0, -90]]
    elif lis_type == "stereo":
        catalog_center_list = [(ra, dec) for ra in range(0, 360, distance) for dec in range(-85, 90, distance)] + [(0, 90), (0, -90)]
    else:
        return NameError("ERROR: See function get_catalog_center_points")
    return catalog_center_list


def map_match_and_radec_list_multiprocess(ra_dec_list, lis_type="rpi"):
    """
    Apply 'call_match' multiprocessing depending on numbers of cores.
    """
    n_cores = multiprocessing.cpu_count()
    if n_cores == 1:
        if lis_type == "rpi":
            first_match_results = map(call_match_list, ra_dec_list)
        else:
            first_match_results = map(lambda p: call_match_list(p, lis_type="stereo"), ra_dec_list)
    else:
        pool = multiprocessing.Pool(n_cores)
        if lis_type == "rpi":
            first_match_results = pool.map(call_match_list, ra_dec_list)
        else:
            first_match_results = pool.starmap(call_match_list, zip(ra_dec_list, repeat("stereo")))
    return first_match_results


def call_match_list(ra_dec_list, lis_type="rpi", base='catalog'):
    """
    Call 'Match' with RA/DEC list in the shell.
    """
    ra, dec = ra_dec_list
    if base == 'catalog':
        if lis_type == "rpi":
            match = set_match_str(ra, dec, DIR_STARS, DIR_PROJ_CAT_RPI, PARAM1)
        elif lis_type == "stereo":
            match = set_match_str(ra, dec, DIR_STARS, DIR_PROJ_CAT_STEREO, PARAM1)
        else:
            raise NameError("ERROR: See function call_match_list ")
        # print(match)
    elif base == 'picture':
        if lis_type == "rpi":
            match = set_match_str(ra, dec, DIR_STARS, DIR_PROJ_CAT_RPI, PARAM1, base='picture')
        elif lis_type == "stereo":
            match = set_match_str(ra, dec, DIR_STARS, DIR_PROJ_CAT_STEREO, PARAM1, base='picture')
        else:
            raise NameError("ERROR: See function call_match_list ")
    else:
        raise NameError("---> ERROR: Select a valid base for Match!")
    status, result = sp.getstatusoutput(match)
    return status, result


def set_match_str(ra, dec, dir_stars, dir_proj_cat, param, base='catalog'):
    """
    Define and set the 'match' string before calling it in the shell.
    """
    ra_dec_str = "cat_RA_{}_DEC_{}".format(ra, dec)
    if base == 'catalog':
        match_str = "match {} 0 1 2 {}/{} 0 1 2 {}".format(dir_stars, dir_proj_cat, ra_dec_str, param)
        # print(match_str)
    elif base == 'picture':
        match_str = "match {}/{} 0 1 2 {} 0 1 2 {}".format(dir_proj_cat, ra_dec_str, dir_stars, param)
    else:
        raise NameError("---> ERROR: Select a valid base for Match!")
    return match_str


def get_table_with_matchs(ra_dec_list, first_match_results):
    """
    Select RA/DEC values in which a successful match was obtained, and generate a 'match' table.
    """
    match_table = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))
    for i, (status, result) in enumerate(first_match_results):
        if status == 0:
            ra, dec = ra_dec_list[i]
            regexp_result = MATCH_STD.findall(result)[0]
            sig = float(regexp_result[0])
            nr = int(regexp_result[1])
            match_table.add_row([str(ra), str(dec), sig, nr])
    if len(match_table) == 0:
        print("--> After search in the whole catalog, I can not find any match between picture and catalog! :(")
        raise ValueError("---> ERROR: There is no match ...")
    else:
        match_table.sort('Nr')
        match_table.reverse()
    return match_table


def get_match_candidates(match_table):
    """
    Select three 'match' candidates from 'first match table'.
    """
    len_table = len(match_table)
    if len_table == 1:
        match_candidates = match_table
    elif len_table == 2:
        match_candidates = match_table
    else:
        match_candidates = match_table[0:3]
    return match_candidates


def get_first_match_data(candidates, try_n, lis_type="rpi", base="catalog"):
    """
    With a list of 'match candidates', recall match to obtain the transformation relationship.
    """
    cand = candidates[try_n]
    if base == "catalog":
        if lis_type == "rpi":
            result = call_match_list([int(cand[0]), int(cand[1])])[1]
        elif lis_type == "stereo":
            result = call_match_list([int(cand[0]), int(cand[1])], lis_type="stereo")[1]
        else:
            raise NameError("ERROR: See function get_first_match_data")
    elif base == "picture":
        print("Base is picture!")
        if lis_type == "rpi":
            result = call_match_list([int(cand[0]), int(cand[1])], base="picture")[1]
        elif lis_type == "stereo":
            result = call_match_list([int(cand[0]), int(cand[1])], lis_type="stereo", base="picture")[1]
        else:
            raise NameError("ERROR")
    else:
        raise ValueError("---> ERROR: Select a valid base for Match!")
    regexp_result_numbers = MATCH_NUMBERS.findall(result)[0]
    regexp_result_std = MATCH_STD.findall(result)[0]
    return regexp_result_numbers, regexp_result_std


def apply_match_trans(data):
    """
    Apply the 'match' transformation between picture and projected catalog.
    This is: center of picture (pix) ==> point in the projected catalog (mm).
    """
    match_a = float(data[0])
    match_b = float(data[1])
    match_c = float(data[2])
    match_d = float(data[3])
    match_ra_mm, match_dec_mm = match_a, match_d
    match_roll_rad = np.arctan2(match_c, match_b)
    match_roll_deg = np.rad2deg(match_roll_rad)
    return match_ra_mm, match_dec_mm, match_roll_deg


def plane2sky(ra_match_mm, dec_match_mm, ra_catalog, dec_catalog, lis_type="rpi"):
    """
    Deproject any arbitrary point in the camera. This is: mm ==> sky coordinates.
    """
    if lis_type == "rpi":
        focal_len_mm = FOCAL_LEN_MM_RPI
    elif lis_type == "stereo":
        focal_len_mm = FOCAL_LEN_MM_STEREO
    else:
        raise NameError("ERROR")
    xi = ra_match_mm / float(focal_len_mm)
    eta = dec_match_mm / float(focal_len_mm)
    dec_catalog_rad = np.deg2rad(dec_catalog)
    arg1 = np.cos(dec_catalog_rad) - eta * np.sin(dec_catalog_rad)
    arg2 = np.arctan(xi / arg1)
    arg3 = np.sin(arg2)
    arg4 = eta * np.cos(dec_catalog_rad) + np.sin(dec_catalog_rad)
    alpha = ra_catalog + np.rad2deg(arg2)
    delta = np.rad2deg(np.arctan((arg3 * arg4) / xi))
    return alpha, delta


def search_catalog_objects(ra_first_match, dec_first_match, lis_type="rpi"):
    """
    Search in the normal catalog for all sky-objects (to the nearest catalog), and create a table.
    """
    if lis_type == "rpi":
        ra_catalog = int(round(ra_first_match))
        dec_catalog = int(round(dec_first_match))
        new_cat_name = "{}/cat_RA_{}_DEC_{}".format(DIR_NORMAL_CAT_RPI, ra_catalog, dec_catalog)
    elif lis_type == "stereo":
        ra_catalog = int(5 * round(float(ra_first_match)/5))
        dec_catalog = int(5* round(float(dec_first_match)/5))
        new_cat_name = "{}/cat_RA_{}_DEC_{}".format(DIR_NORMAL_CAT_STEREO, ra_catalog, dec_catalog)
    else:
        raise NameError("ERROR: See function search_catalog_objects")
    new_cat = ascii.read(new_cat_name)
    noproj_table = Table([[], [], []])
    for ii in range(len(new_cat)):
        noproj_table.add_row([new_cat[ii][0], new_cat[ii][1], new_cat[ii][2]])
    return noproj_table


def sky2plane(star_list, ra_project_point, dec_project_point, lis_type="rpi"):
    """
    With a list of 'matched' stars, project all in the tangent plane.
    """
    cat_projected = Table([[], [], []])
    stars_len = len(star_list)
    if lis_type == "rpi":
        focal_len_mm = FOCAL_LEN_MM_RPI
    elif lis_type == "stereo":
        focal_len_mm = FOCAL_LEN_MM_STEREO
    else:
        raise NameError("ERROR: See function sky2plane")
    for index in range(stars_len):
        alpha_deg = star_list[index][0]
        delta_deg = star_list[index][1]
        mag = star_list[index][2]
        alpha_rad = np.deg2rad(alpha_deg)
        delta_rad = np.deg2rad(delta_deg)
        alpha_0_rad = np.deg2rad(ra_project_point)
        delta_0_rad = np.deg2rad(dec_project_point)
        xi_up = np.cos(delta_rad) * np.sin(alpha_rad - alpha_0_rad)
        xi_down = np.sin(delta_0_rad) * np.sin(delta_rad)\
            + np.cos(delta_0_rad) * np.cos(delta_rad) * np.cos(alpha_rad - alpha_0_rad)
        xi = xi_up/xi_down
        eta_up = np.cos(delta_0_rad) * np.sin(delta_rad)\
            - np.sin(delta_0_rad) * np.cos(delta_rad) * np.cos(alpha_rad - alpha_0_rad)
        eta_down = xi_down
        eta = eta_up / eta_down
        xi_mm = xi * focal_len_mm
        eta_mm = eta * focal_len_mm
        cat_projected.add_row([xi_mm, eta_mm, mag])
    cat_name = 'new_cat'
    ascii.write(cat_projected, cat_name, delimiter=' ', format='no_header', overwrite=True,
                formats={'X': '% 15.5f', 'Y': '% 15.5f', 'Z': '% 15.2f'}, names=['X', 'Y', 'Z'])
    return 0


def call_match_once(base="catalog", outfile=None):
    """
    Call 'Match' one time, in further 'match' iterations.
    """
    if base == "catalog":
        match_str = "match {} 0 1 2 {} 0 1 2 {}".format(DIR_STARS, NEW_PROJ_CAT, PARAM2)
    elif base == "picture":
        match_str = "match {} 0 1 2 {} 0 1 2 {}".format(NEW_PROJ_CAT, DIR_STARS, PARAM2)
    else:
        raise ValueError("---> ERROR: Select a valid base for Match!")
    # print(match_str)
    if outfile is not None:
        match_str = match_str + ' outfile=' + outfile
    status, result = sp.getstatusoutput(match_str)
    # print("Status: ", status)
    # print("Result: ", result)
    regexp_result_numbers = MATCH_NUMBERS.findall(result)[0]
    regexp_result_std = MATCH_STD.findall(result)[0]
    return regexp_result_numbers, regexp_result_std


def solve_lis(img_full_dir, catalog_division, stt_data_dir, lis_type="rpi"):
    """
    Solve the Lost-In-Space problem.
    """
    tm1 = time.time()
    # Apply SExtractor.
    if lis_type == "rpi":
        str_fits = "img.fits"
        img_fits_name = "{}/{}".format(stt_data_dir, str_fits)
        jpg2fits(img_full_dir, img_fits_name)
    elif lis_type == "stereo":
        str_fits = img_full_dir
    else:
        raise NameError("ERROR: Please introduce a valid lis_type parameter <rpi> or <stereo>")
    apply_sextractor(str_fits, stt_data_dir, lis_type)
    # Apply Match - First iteration.
    ra_dec_list = get_catalog_center_points(0, 0, catalog_division, lis_type)
    first_match_map_results = map_match_and_radec_list_multiprocess(ra_dec_list, lis_type)
    first_match_table = get_table_with_matchs(ra_dec_list, first_match_map_results)
    # print(first_match_table)
    match_candidates = get_match_candidates(first_match_table)
    print("\n---> Match candidates:")
    print(match_candidates)
    attempts = 0
    third_alpha, third_delta, third_roll_deg, third_match_std = (0, 0, 0, [0, 0])
    while attempts < LIS_MAX_ITER:
        try:
            first_ra_catalog, first_dec_catalog = match_candidates[attempts][0], match_candidates[attempts][1]
            # print("{} {} {}".format(attempts, first_ra_catalog, first_dec_catalog))
            first_match_data, first_match_std = get_first_match_data(match_candidates, attempts, lis_type)
            first_ra_mm, first_dec_mm, first_roll_deg = apply_match_trans(first_match_data)
            first_alpha, first_delta = plane2sky(first_ra_mm, first_dec_mm, first_ra_catalog, first_dec_catalog, lis_type)
            # Apply Match - Second and third iteration.
            noproj_table = search_catalog_objects(first_alpha, first_delta, lis_type)
            sky2plane(noproj_table, first_alpha, first_delta, lis_type)
            second_match_data, second_match_std = call_match_once()
            second_ra_mm, second_dec_mm, second_roll_deg = apply_match_trans(second_match_data)
            second_alpha, second_delta = plane2sky(second_ra_mm, second_dec_mm, first_alpha, first_delta, lis_type)
            sky2plane(noproj_table, second_alpha, second_delta, lis_type)
            third_match_data, third_match_std = call_match_once()
            third_ra_mm, third_dec_mm, third_roll_deg = apply_match_trans(third_match_data)
            third_alpha, third_delta = plane2sky(third_ra_mm, third_dec_mm, second_alpha, second_delta, lis_type)
            # third_alpha_normalized, third_roll_deg_normalized = normalize_coord(third_alpha, third_roll_deg)
            break
        except Exception as err:
            attempts += 1
            print('---> ERROR: {}'.format(err))
    if attempts == LIS_MAX_ITER:
        raise ValueError("---> ERROR: After {} attempts to find a match, it can not be done :(".format(LIS_MAX_ITER))
    # Print final results.
    tm2 = time.time()
    exec_time = tm2 - tm1
    print("\n---> ATTITUDE SOLUTION:\n RA   = {:.4f}°\n DEC  = {:.4f}°\n Roll = {:.4f}°\n Exec time = {:.4f} s".format(
        third_alpha, third_delta, third_roll_deg, exec_time))
    return third_alpha, third_delta, third_roll_deg, third_match_std[0], third_match_std[1]
