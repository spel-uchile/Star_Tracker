import multiprocessing
import numpy as np
import os
import platform
import re
import subprocess as sp
import time
from astropy.io import fits, ascii
from astropy.table import Table
from PIL import Image

EXEC_DIR = 'RPi'  # It can be <RPi> or <PC>

# CONSTANT VALUES.
x_pix = 512
y_pix = 512
pix2mm = 0.002695
focal_len_mm = 3.04
# DIRECTORIES.
DIR_stars = 'sext'
if EXEC_DIR == 'RPi':
    DIR_proj_cat = '/home/pi/RA_DEC_V2/Proyectado/cat_RA_'
    dir_normal_cat = '/home/pi/RA_DEC_V2/Normal/'
elif EXEC_DIR == 'PC':
    DIR_proj_cat = '/home/samuel/Desktop/SPEL/3_Star_Tracker/Division_de_catalogo/Scripts/Catalogo_dividido_y_proyectado/RA_DEC_V2/Proyectado/cat_RA_'
    dir_normal_cat = '/home/samuel/Desktop/SPEL/3_Star_Tracker/Division_de_catalogo/Scripts/Catalogo_dividido_y_proyectado/RA_DEC_V2/Normal/'
else:
    raise NameError('ERROR: Please select a correct EXEC_DIR: <RPi> or <PC>')
new_proj_cat = 'new_cat'
# MATCH PARAMETERS.
param1 = 'trirad=0.002 nobj=15 max_iter=1 matchrad=0.1 scale=1'
param2 = 'trirad=0.002 nobj=20 max_iter=5 matchrad=0.01 scale=1'
# REGULAR EXPRESSIONS.
match_std_search = re.compile(r"sig=(-*\d\.\d+e...) Nr=(-*\d+) Nm=(-*\d+) sx=(-*\d\.\d+e...) sy=(-*\d\.\d+e...)")
match_numbers_search = re.compile(r"a=(-*\d\.\d+e...) b=(-*\d\.\d+e...) c=(-*\d\.\d+e...) "
                                  r"d=(-*\d\.\d+e...) e=(-*\d\.\d+e...) f=(-*\d\.\d+e...)")
# Another relevant parameters
LIS_MAX_ITER = 3
SEXTRACTOR_MAX_STARS = 40
SEXTRACTOR_STR = "sextractor"


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


def apply_sextractor(img_fits_name, stt_data_dir):
    """
    Apply Source Extractor over an image and generates a catalog.
    """
    os.chdir(stt_data_dir)
    sext_task = "{} {}".format(SEXTRACTOR_STR, img_fits_name)
    sp.check_output(sext_task, shell=True)
    sext1 = ascii.read('./test.cat', format='sextractor')
    sext1.sort(['MAG_ISO'])
    sext2 = sext1[0:SEXTRACTOR_MAX_STARS]
    sext_x_pix = sext2['X_IMAGE']
    sext_y_pix = sext2['Y_IMAGE']
    sext_mag = sext2['MAG_ISO']
    sext_x_mm = (sext_x_pix - x_pix) * pix2mm
    sext_y_mm = (sext_y_pix - y_pix) * pix2mm
    sext_filename = 'sext'
    ascii.write([sext_x_mm, sext_y_mm, sext_mag], sext_filename, delimiter=' ', format='no_header', overwrite=True,
                formats={'X': '% 15.10f', 'Y': '% 15.10f', 'Z': '% 15.10f'}, names=['X', 'Y', 'Z'])
    return sext_x_pix, sext_y_pix, sext_x_mm, sext_y_mm


def apply_sextractor_test(img_fits_name, sext_dir, catalog_name):
    """
    Apply Source Extractor over an image and generates a catalog.
    """
    os.chdir(sext_dir)
    sext_task = "{} {}".format(SEXTRACTOR_STR, img_fits_name)
    sp.check_output(sext_task, shell=True)
    sext1 = ascii.read('./test.cat', format='sextractor')
    sext1.sort(['MAG_ISO'])
    sext2 = sext1[0:SEXTRACTOR_MAX_STARS]
    sext_x_pix = sext2['X_IMAGE']
    sext_y_pix = sext2['Y_IMAGE']
    sext_mag = sext2['MAG_ISO']
    sext_filename = catalog_name
    ascii.write([sext_x_pix, sext_y_pix, sext_mag], sext_filename, delimiter=' ', format='no_header', overwrite=True,
                formats={'X': '% 15.5f', 'Y': '% 15.5f', 'Z': '% 15.5f'}, names=['X', 'Y', 'Z'])
    return 0


def apply_sextractor_in_exp_time_evaluation(img_fits_name, stt_data_dir):
    """
    Apply Source Extractor over an image and get extractions number.
    """
    os.chdir(stt_data_dir)
    sext_task = "{} {}".format(SEXTRACTOR_STR, img_fits_name)
    sp.check_output(sext_task, shell=True)
    sext1 = ascii.read('./test.cat', format='sextractor')
    sext1.sort(['MAG_ISO'])
    extracted_objects = len(sext1)
    return extracted_objects


def get_catalog_center_points(x_center, y_center, distance):
    """
    Get the center points for different catalogs segments, for a given distance and starting point.
    It consider declination of center site.
    """
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
    return catalog_center_list


def call_match_list(ra_dec_list, base='catalog'):
    """
    Call 'Match' with RA/DEC list in the shell.
    """
    ra, dec = ra_dec_list
    if base == 'catalog':
        match = set_match_str(ra, dec, DIR_stars, DIR_proj_cat, param1)
        # print(match)
    elif base == 'picture':
        match = set_match_str(ra, dec, DIR_stars, DIR_proj_cat, param1, base='picture')
    else:
        raise ValueError('==> ERROR: Select a valid base for Match!')
    status, result = sp.getstatusoutput(match)
    return status, result


def set_match_str(ra, dec, dir_stars, dir_proj_cat, param, base='catalog'):
    """
    Define and set the 'match' string before calling it in the shell.
    """
    ra_dec_str = "{}_DEC_{}".format(ra, dec)
    if base == 'catalog':
        match_str = "match {} 0 1 2 {}{} 0 1 2 {}".format(dir_stars, dir_proj_cat, ra_dec_str, param)
        # print(match_str)
    elif base == 'picture':
        match_str = "match {}{} 0 1 2 {} 0 1 2 {}".format(dir_proj_cat, ra_dec_str, dir_stars, param)
    else:
        raise ValueError('==> ERROR: Select a valid base for Match!')
    return match_str


def map_match_and_radec_list_multiprocess(ra_dec_list):
    """
    Apply 'call_match' multiprocessing depending on numbers of cores.
    """
    n_cores = multiprocessing.cpu_count()
    if n_cores == 1:
        first_match_results = map(call_match_list, ra_dec_list)
    else:
        pool = multiprocessing.Pool(n_cores)
        first_match_results = pool.map(call_match_list, ra_dec_list)
    return first_match_results


def get_table_with_matchs(ra_dec_list, first_match_results):
    """
    Select RA/DEC values in which a successful match was obtained, and generate a 'match' table.
    """
    match_table = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))
    for i, (status, result) in enumerate(first_match_results):
        if status == 0:
            ra, dec = ra_dec_list[i]
            regexp_result = match_std_search.findall(result)[0]
            sig = float(regexp_result[0])
            nr = int(regexp_result[1])
            match_table.add_row([str(ra), str(dec), sig, nr])
    if len(match_table) == 0:
        print('--> After search in the whole catalog, I can not find any match between picture and catalog! :(')
        raise ValueError('There is no match ...')
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
        short_match_table = match_table[0:3]
        match_candidates = short_match_table
    return match_candidates


def get_first_match_data(candidates, try_n, base='catalog'):
    """
    With a list of 'match candidates', recall match to obtain the transformation relationship.
    """
    cand = candidates[try_n]
    if base == 'catalog':
        result = call_match_list([int(cand[0]), int(cand[1])])[1]
    elif base == 'picture':
        print('Base is picture!')
        result = call_match_list([int(cand[0]), int(cand[1])], base='picture')[1]
    else:
        raise ValueError('==> ERROR: Select a valid base for Match!')
    regexp_result_numbers = match_numbers_search.findall(result)[0]
    regexp_result_std = match_std_search.findall(result)[0]
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


def plane2sky(ra_match_mm, dec_match_mm, ra_catalog, dec_catalog):
    """
    Deproject any arbitrary point in the camera. This is: mm ==> sky coordinates.
    """
    xi = ra_match_mm/float(focal_len_mm)
    eta = dec_match_mm/float(focal_len_mm)
    dec_catalog_rad = np.deg2rad(dec_catalog)
    arg1 = np.cos(dec_catalog_rad) - eta * np.sin(dec_catalog_rad)
    arg2 = np.arctan(xi / arg1)
    arg3 = np.sin(arg2)
    arg4 = eta * np.cos(dec_catalog_rad) + np.sin(dec_catalog_rad)
    alpha = ra_catalog + np.rad2deg(arg2)
    delta = np.rad2deg(np.arctan((arg3 * arg4) / xi))
    return alpha, delta


def search_catalog_objects(ra_first_match, dec_first_match):
    """
    Search in the normal catalog for all sky-objects (to the nearest catalog), and create a table.
    """
    ra_catalog = int(round(ra_first_match))
    dec_catalog = int(round(dec_first_match))
    new_cat_name = dir_normal_cat + 'cat_RA_' + str(int(ra_catalog)) + '_DEC_' + str(int(dec_catalog))
    new_cat = ascii.read(new_cat_name)
    noproj_table = Table([[], [], []])
    for ii in range(len(new_cat)):
        noproj_table.add_row([new_cat[ii][0], new_cat[ii][1], new_cat[ii][2]])
    return noproj_table


def sky2plane(star_list, ra_project_point, dec_project_point):
    """
    With a list of 'matched' stars, project all in the tangent plane.
    """
    cat_projected = Table([[], [], []])
    stars_len = len(star_list)
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


def call_match_once(base='catalog', outfile=None):
    """
    Call 'Match' one time, in further 'match' iterations.
    """
    if base == 'catalog':
        match_str = 'match ' + DIR_stars + ' 0 1 2 ' + new_proj_cat + ' 0 1 2 ' + param2
    elif base == 'picture':
        match_str = 'match ' + new_proj_cat + ' 0 1 2 ' + DIR_stars + ' 0 1 2 ' + param2
    else:
        raise ValueError('==> ERROR: Select a valid base for Match!')
    # print(match_str)
    if outfile is not None:
        match_str = match_str + ' outfile=' + outfile
    status, result = sp.getstatusoutput(match_str)
    # print('Status: ', status)
    # print('Result: ', result)
    regexp_result_numbers = match_numbers_search.findall(result)[0]
    regexp_result_std = match_std_search.findall(result)[0]
    return regexp_result_numbers, regexp_result_std


def sextractor_test(folder_dir, img_full_dir, catalog_name):
    """
    Apply sextractor test over an image
    """
    str_fits = "img.fits"
    img_fits_name = "{}/{}".format(folder_dir, str_fits)
    jpg2fits(img_full_dir, img_fits_name)
    apply_sextractor_test(str_fits, folder_dir, catalog_name)
    return 0


def solve_lis(img_full_dir, picture_time, catalog_division, stt_data_dir):
    """
    Solve the Lost-In-Space problem, in a SIMPLE way
    """
    tm1 = time.time()
    # Apply SExtractor.
    str_fits = "img.fits"
    img_fits_name = "{}/{}".format(stt_data_dir, str_fits)
    jpg2fits(img_full_dir, img_fits_name)
    apply_sextractor(str_fits, stt_data_dir)
    # Apply Match - First iteration.
    ra_dec_list = get_catalog_center_points(0, 0, catalog_division)
    first_match_map_results = map_match_and_radec_list_multiprocess(ra_dec_list)
    first_match_table = get_table_with_matchs(ra_dec_list, first_match_map_results)
    # print(first_match_table)
    match_candidates = get_match_candidates(first_match_table)
    print(match_candidates)
    attempts = 0
    while attempts < LIS_MAX_ITER:
        try:
            first_ra_catalog, first_dec_catalog = match_candidates[attempts][0], match_candidates[attempts][1]
            # print('{} {} {}'.format(attempts, first_ra_catalog, first_dec_catalog))
            first_match_data, first_match_std = get_first_match_data(match_candidates, attempts)
            first_ra_mm, first_dec_mm, first_roll_deg = apply_match_trans(first_match_data)
            first_alpha, first_delta = plane2sky(first_ra_mm, first_dec_mm, first_ra_catalog, first_dec_catalog)
            # Apply Match - Second and third iteration.
            noproj_table = search_catalog_objects(first_alpha, first_delta)
            sky2plane(noproj_table, first_alpha, first_delta)
            second_match_data, second_match_std = call_match_once()
            second_ra_mm, second_dec_mm, second_roll_deg = apply_match_trans(second_match_data)
            second_alpha, second_delta = plane2sky(second_ra_mm, second_dec_mm, first_alpha, first_delta)
            sky2plane(noproj_table, second_alpha, second_delta)
            third_match_data, third_match_std = call_match_once()
            third_ra_mm, third_dec_mm, third_roll_deg = apply_match_trans(third_match_data)
            third_alpha, third_delta = plane2sky(third_ra_mm, third_dec_mm, second_alpha, second_delta)
            # third_alpha_normalized, third_roll_deg_normalized = normalize_coord(third_alpha, third_roll_deg)
            break
        except Exception as err:
            attempts += 1
            print('---> ERROR: {}'.format(err))
    if attempts == LIS_MAX_ITER:
        raise ValueError('--> ERROR: After three attempts to find a match, it can not be done :(')
    # Print final results.
    tm2 = time.time()
    exec_time = tm2 - tm1
    print("===> SOLUTION: RA = {:.4f} / DEC = {:.4f} / Roll = {:.4f} / Timestamp = {} / Execution time = {:.4f}".format(
        third_alpha, third_delta, third_roll_deg, picture_time, exec_time))
    lis_dir = "{}/lis_one_image.txt".format(stt_data_dir)
    with open(lis_dir, "w")as f:
        f.write("{:.4f} {:.4f} {:.4f} {} {:.4f}".format(
            third_alpha, third_delta, third_roll_deg, picture_time, exec_time))
    return third_alpha, third_delta, third_roll_deg, third_match_std[0], third_match_std[1]


def normalize_coord(ra, roll):
    """
    Set the RA and Roll coordinates in a standard way (like STEREO way!).
    """
    if ra > 180.0:
        ra_out = ra - 360.0
    else:
        ra_out = ra
    if roll < 0.0:
        roll_out = roll + 180.0
    else:
        roll_out = roll - 180.0
    return ra_out, roll_out


def solve_lis_problem(image_full_dir, catalog_division, stt_data_dir, mod=False):
    """
    Read an image and solve the full LIS problem.
    """
    try:
        # 1.- Read .jpg image and transform it to .fits.
        str_fits = "img.fits"
        img_fits_dir = "{}/{}".format(stt_data_dir, str_fits)
        jpg2fits(image_full_dir, img_fits_dir)
        # 2.- Apply SEx.
        apply_sextractor(str_fits, stt_data_dir)
        # 3.A.- Apply Match - First iteration.
        ra_dec_list = get_catalog_center_points(0, 0, catalog_division)
        first_match_map_results = map_match_and_radec_list_multiprocess(ra_dec_list)
        first_match_table = get_table_with_matchs(ra_dec_list, first_match_map_results)
        match_candidates = get_match_candidates(first_match_table)
        first_ra_catalog, first_dec_catalog = match_candidates[0][0], match_candidates[0][1]
        first_match_data, first_match_std = get_first_match_data(match_candidates, 0)
        first_ra_mm, first_dec_mm, first_roll_deg = apply_match_trans(first_match_data)
        first_alpha, first_delta = plane2sky(first_ra_mm, first_dec_mm, first_ra_catalog, first_dec_catalog)
        # 3.B.- Apply Match - Second and third iteration.
        noproj_table = search_catalog_objects(first_alpha, first_delta)
        sky2plane(noproj_table, first_alpha, first_delta)
        second_match_data, second_match_std = call_match_once()
        second_ra_mm, second_dec_mm, second_roll_deg = apply_match_trans(second_match_data)
        second_alpha, second_delta = plane2sky(second_ra_mm, second_dec_mm, first_alpha, first_delta)
        sky2plane(noproj_table, second_alpha, second_delta)
        third_match_data, third_match_std = call_match_once()
        third_ra_mm, third_dec_mm, third_roll_deg = apply_match_trans(third_match_data)
        third_alpha, third_delta = plane2sky(third_ra_mm, third_dec_mm, second_alpha, second_delta)
        if mod is False:
            third_alpha_normalized, third_roll_deg_normalized = normalize_coord(third_alpha, third_roll_deg)
        else:
            third_alpha_normalized = third_alpha
            _, third_roll_deg_normalized = normalize_coord(third_alpha, third_roll_deg)
        nr = third_match_std[1]
    except Exception as err:
        print('--> ERROR: ', err)
        third_alpha_normalized, third_delta, third_roll_deg_normalized, nr = (0, 0, 0, 0)
    return third_alpha_normalized, third_delta, third_roll_deg_normalized, nr


def get_reduced_catalogs(ra_center, dec_center, delta=5):
    """
    Get the catalogs closest to the central point of the image to reduce the search once we solved the LIS problem.
    """
    try:
        # Transform to integers.
        ra_center = int(ra_center)
        dec_center = int(dec_center)
        # Check if the (ra, dec) centers have valid values.
        if ra_center < 0 or ra_center >= 360:
            raise ValueError('--> ERROR:  0 <= ra_center < 360 !')
        if dec_center < -90 or dec_center > 90:
            raise ValueError('--> ERROR: -90 <= dec_center <= 90 !')
        # Compute the distance to the nearest catalog considering declination.
        dec_center_up = dec_center + delta
        dec_center_down = dec_center - delta
        delta_center = int(delta / np.cos(np.deg2rad(dec_center)))
        delta_up = int(delta / np.cos(np.deg2rad(dec_center_up)))
        delta_down = int(delta / np.cos(np.deg2rad(dec_center_down)))
        # Compute the ra points considering the delta due to the declination.
        ra_center_left = ra_center - delta_center
        ra_center_right = ra_center + delta_center
        ra_down_left = ra_center - delta_down
        ra_down_right = ra_center + delta_down
        ra_up_left = ra_center - delta_up
        ra_up_right = ra_center + delta_up
        # Check if the computed numbers are valid values for RA. If not, correct the numbers.
        if ra_center_left < 0:
            ra_center_left = 360 + ra_center_left
        if ra_up_left < 0:
            ra_up_left = 360 + ra_up_left
        if ra_down_left < 0:
            ra_down_left = 360 + ra_down_left
        if ra_center_right >= 360:
            ra_center_right = ra_center_right - 360
        if ra_up_right >= 360:
            ra_up_right = ra_up_right - 360
        if ra_down_right >= 360:
            ra_down_right = ra_down_right - 360
        # Generates the 9 (nine) pair of points to form a 'grid' of center of catalogs.
        pair1 = [ra_center, dec_center]
        pair2 = [ra_center, dec_center_down]
        pair3 = [ra_center, dec_center_up]
        pair4 = [ra_center_left, dec_center]
        pair5 = [ra_center_right, dec_center]
        pair6 = [ra_down_left, dec_center_down]
        pair7 = [ra_down_right, dec_center_down]
        pair8 = [ra_up_left, dec_center_up]
        pair9 = [ra_up_right, dec_center_up]
        if -80 <= dec_center <= 80:
            reduced_catalogs = [pair1, pair2, pair3, pair4, pair5, pair6, pair7, pair8, pair9]
        # Correct the grid for points near the celestial poles (DEC > 80 or DEC < -80).
        elif 80 < dec_center < 90:
            pair3 = [0, 90]
            reduced_catalogs = [pair1, pair2, pair3, pair4, pair5, pair6, pair7]
        elif -80 > dec_center > -90:
            pair2 = [0, -90]
            reduced_catalogs = [pair1, pair2, pair3, pair4, pair5, pair8, pair9]
        elif dec_center == 90:
            pair1 = [0, 90]
            reduced_catalogs = [pair1, pair2, pair6, pair7]
        elif dec_center == -90:
            pair1 = [0, -90]
            reduced_catalogs = [pair1, pair3, pair8, pair9]
        else:
            raise ValueError('--> Unknown ERROR: Please check the function <<get_reduced_catalogs>>')
    except Exception as err:
        print(err)
        reduced_catalogs = list()
    return reduced_catalogs


def solve_tracking_problem(image_full_dir, ra_center, dec_center, stt_data_dir):
    """
    Read an image and solve the tracking problem, using a previously known center.
    """
    try:
        # 1.- Read .jpg image and transform it to .fits.
        str_fits = "img.fits"
        img_fits_dir = "{}/{}".format(stt_data_dir, str_fits)
        jpg2fits(image_full_dir, img_fits_dir)
        # 2.- Apply SEx.
        apply_sextractor(str_fits, stt_data_dir)
        # 3.A.- Apply Match - First iteration.
        ra_dec_list = get_reduced_catalogs(ra_center, dec_center)
        first_match_map_results = map_match_and_radec_list_multiprocess(ra_dec_list)
        first_match_table = get_table_with_matchs(ra_dec_list, first_match_map_results)
        match_candidates = get_match_candidates(first_match_table)
        first_ra_catalog, first_dec_catalog = match_candidates[0][0], match_candidates[0][1]
        first_match_data, first_match_std = get_first_match_data(match_candidates, 0)
        first_ra_mm, first_dec_mm, first_roll_deg = apply_match_trans(first_match_data)
        first_alpha, first_delta = plane2sky(first_ra_mm, first_dec_mm, first_ra_catalog, first_dec_catalog)
        # 3.B.- Apply Match - Second and third iteration.
        noproj_table = search_catalog_objects(first_alpha, first_delta)
        sky2plane(noproj_table, first_alpha, first_delta)
        second_match_data, second_match_std = call_match_once()
        second_ra_mm, second_dec_mm, second_roll_deg = apply_match_trans(second_match_data)
        second_alpha, second_delta = plane2sky(second_ra_mm, second_dec_mm, first_alpha, first_delta)
        sky2plane(noproj_table, second_alpha, second_delta)
        third_match_data, third_match_std = call_match_once()
        third_ra_mm, third_dec_mm, third_roll_deg = apply_match_trans(third_match_data)
        third_alpha, third_delta = plane2sky(third_ra_mm, third_dec_mm, second_alpha, second_delta)
        _, third_roll_deg_normalized = normalize_coord(third_alpha, third_roll_deg)
        nr = third_match_std[1]
    except Exception as err:
        print('--> ERROR: ', err)
        third_alpha, third_delta, third_roll_deg_normalized, nr = (0, 0, 0, 0)
    return third_alpha, third_delta, third_roll_deg_normalized, nr


def save_attitude_data(file_name, string):
    if EXEC_DIR == 'RPi':
        fname = "/home/pi/tracking_data/{}.txt".format(file_name)
    elif EXEC_DIR == 'PC':
        fname = "/home/samuel/tracking_data/{}.txt".format(file_name)
    else:
        raise NameError('ERROR: Please select a correct EXEC_DIR: <RPi> or <PC>')
    with open(fname, 'a') as att:
        att.write(string)
    return 0


def evaluate_exp_time(cam_type, init_time, final_time, time_step, n_stars, stt_data_dir):
    exp_time_ms = []
    extracted_objects_list = []
    img_fits_name = "{}/img_exp_time_eval.fits".format(stt_data_dir)
    for time_ms in range(init_time, final_time, time_step):
        pic_name = "/home/pi/STT_pictures/exp_time_eval_{}ms.jpg".format(time_ms)
        time_micros = 1000 * time_ms
        if cam_type == 1:
            task = 'raspistill -w 1024 -h 1024 -t 1 -ss {} -o {}'.format(time_micros, pic_name)
        elif cam_type == 2:
            task = 'libcamera-still -o {} -t 1 --width 1024 --height 1024 --shutter {}'.format(pic_name, time_micros)
        else:
            raise ValueError('Please select a valid camera command type: <1:raspistill>  or <2:libcamera-still>')
        print('EXECUTING: ', task)
        if EXEC_DIR == 'RPi':
            process = sp.Popen(task, shell=True, stdout=sp.PIPE)
            process.wait()
            return_code = process.returncode
            if return_code != 0:
                raise OSError('The script in the shell was not correctly executed!')
            jpg2fits(pic_name, img_fits_name)
        elif EXEC_DIR == 'PC':
            pic_name = "{}/sample_pic.jpg".format(stt_data_dir)
            jpg2fits(pic_name, img_fits_name)
        else:
            raise NameError('ERROR: Please select a correct EXEC_DIR: <RPi> or <PC>')
        extracted_objects = apply_sextractor_in_exp_time_evaluation('img_exp_time_eval.fits', stt_data_dir)
        # extracted_objects = time_micros
        exp_time_ms.append(time_ms)
        extracted_objects_list.append(extracted_objects)
    print(exp_time_ms, extracted_objects_list)
    selector = min(range(len(extracted_objects_list)), key=lambda i: abs(extracted_objects_list[i] - n_stars))
    exp_time_dir = "{}/exp_time.txt".format(stt_data_dir)
    with open(exp_time_dir, "w")as f:
        f.write("{} {}".format(exp_time_ms[selector], extracted_objects_list[selector]))
    return 0
