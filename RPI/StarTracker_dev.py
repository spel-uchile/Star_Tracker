# 1.- Imports.
import ST_functions
import sys

review = False  # True

# 2.- Define directories, names and constants values.
DIRs = ST_functions.names_and_dir()
DIR_this, DIR_img_fits, DIR_stars, DIR_first_match_output, DIR_sext = DIRs[0:5]
DIR_proj_cat1, DIR_proj_cat2, DIR_normal_cat, fits_name = DIRs[5:9]
x_pix, y_pix, cmos2pix, rpi_focal = ST_functions.st_constants()

# 3.- Receives and reviews the initial data.
st_args = sys.argv
len_arg = len(st_args)
pic_name, cat_division = ST_functions.review_init_data(st_args, len_arg)

# I.- First review.
if review:
    print '-*'*50
    print ' *** REVIEW - 1 *** '
    print 'Initial arguments:', st_args
    print 'Image name       :', pic_name
    print 'DIR_this         : ', DIR_this
    print '-*'*50

# 4.- Generate a FITS image and execute Source Extractor over it.
ST_functions.jpg2fits(pic_name, fits_name)
ST_functions.apply_sextractor(DIR_sext, DIR_img_fits, fits_name, x_pix, y_pix, cmos2pix)

# 5.- Apply first 'Match' routine (search over the entire catalog) and delivers a first pointing result.
ra_dec_list = ST_functions.generate_radec_list(cat_division)
first_match_map_results = ST_functions.map_match_and_radec_list_multiprocess(ra_dec_list)
first_match_table = ST_functions.get_table_with_matchs(ra_dec_list, first_match_map_results)
match_candidates = ST_functions.get_match_candidates(first_match_table)
try_number = 0
while try_number < len(match_candidates):
    try:
        if try_number == 0:
            print '-> First attempt with match ...'
        first_ra_catalog = match_candidates[try_number][0]
        first_dec_catalog = match_candidates[try_number][1]
        first_match_data, first_match_std = ST_functions.get_first_match_data(match_candidates, try_number)
        first_match_output_pix = ST_functions.apply_match_trans(first_match_data)
        first_ra_pix, first_dec_pix, first_roll_deg = first_match_output_pix
        first_alpha, first_delta = ST_functions.deproject(rpi_focal, first_ra_pix, first_dec_pix,
                                                          first_ra_catalog, first_dec_catalog)

# II.- Second review.
        if review:
            print '-*'*50
            print ' *** REVIEW - 2 *** '
            print ' --- MATCH TABLE --- '
            print first_match_table
            print ' --- MATCH CANDIDATES TABLE --- '
            print match_candidates
            print ' --- FIRST MATCH OUTPUT --- '
            print 'RA (catalog)  :', first_ra_catalog
            print 'DEC (catalog) :', first_dec_catalog
            print 'RA (pix)      :', first_ra_pix
            print 'DEC (pix)     :', first_dec_pix
            print 'RA (degrees)  :', first_alpha
            print 'DEC (degrees) :', first_delta
            print 'Roll (degrees):', first_roll_deg
            print 'sig           :', first_match_std[0]
            print 'Nr            :', first_match_std[1]
            print '-*'*50

# 6.- With the aid of the first result, try a second 'match' to refine the pointing solution.
        noproj_table = ST_functions.search_catalog_objects(DIR_normal_cat, first_ra_catalog, first_dec_catalog)
        ST_functions.sky2plane(noproj_table, first_alpha, first_delta, rpi_focal)
        second_match_data, second_match_std = ST_functions.call_match_once(DIR_stars, DIR_first_match_output)
        second_match_output_pix = ST_functions.apply_match_trans(second_match_data)
        second_ra_pix, second_dec_pix, second_roll_deg = second_match_output_pix
        second_alpha, second_delta = ST_functions.deproject(rpi_focal, second_ra_pix, second_dec_pix,
                                                            first_alpha, first_delta)

# III.- Third review.
        if review:
            print '-*'*50
            print ' *** REVIEW - 3 *** '
            print ' --- NORMAL CATALOG COINCIDENCES --- '
            print noproj_table
            print 'TABLE LENGTH:', len(noproj_table)
            print ' --- SECOND MATCH OUTPUT --- '
            print 'RA (pix)      :', second_ra_pix
            print 'DEC (pix)     :', second_dec_pix
            print 'RA (degrees)  :', second_alpha
            print 'DEC (degrees) :', second_delta
            print 'Roll (degrees):', second_roll_deg
            print 'sig           :', second_match_std[0]
            print 'Nr            :', second_match_std[1]
            print '-*'*50

# 7.- With the aid of the second result, try a third and final 'match' and get the pointing result.
        ST_functions.sky2plane(noproj_table, second_alpha, second_delta, rpi_focal)
        third_match_data, third_match_std = ST_functions.call_match_once(DIR_stars, DIR_first_match_output)
        third_match_output_pix = ST_functions.apply_match_trans(third_match_data)
        third_ra_pix, third_dec_pix, third_roll_deg = third_match_output_pix
        third_alpha, third_delta = ST_functions.deproject(rpi_focal, third_ra_pix, third_dec_pix,
                                                          second_alpha, second_delta)
        third_alpha, third_roll_deg = ST_functions.normalize_coord(third_alpha, third_roll_deg)

# 8.- Print final pointing results.
        print '-*' * 50
        print ' --- THIRD (FINAL) MATCH OUTPUT --- '
        print 'RA (pix)      :', third_ra_pix
        print 'DEC (pix)     :', third_dec_pix
        print 'RA (degrees)  :', third_alpha
        print 'DEC (degrees) :', third_delta
        print 'Roll (degrees):', third_roll_deg
        print 'sig           :', third_match_std[0]
        print 'Nr            :', third_match_std[1]
        print '-*' * 50
        print ' --- THIS SCRIPT HAS FINISHED --- '
        break
    except IndexError:
        if try_number == 0:
            print '-> Second attempt with match ...'
        elif try_number == 1:
            print '-> Last attempt with match ...'
        else:
            raise ValueError('Sorry, the program can not find any match between picture and catalog.')
        try_number += 1
