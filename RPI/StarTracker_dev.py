# 1.- Imports.
import ST_functions
import sys

review = True

# 2.- Define directories, names and constants values.
DIRs = ST_functions.names_and_dir()
DIR_this = DIRs[0]
DIR_img_fits = DIRs[1]
DIR_stars = DIRs[2]
DIR_first_match = DIRs[3]
DIR_sext = DIRs[4]
DIR_proj_cat1 = DIRs[5]
DIR_proj_cat2 = DIRs[6]
DIR_normal_cat = DIRs[7]
fits_name = DIRs[8]
const = ST_functions.st_constants()
x_pix = const[0]
y_pix = const[1]
cmos2pix = const[2]
rpi_focal = const[3]

# 3.- Receives and reviews the initial data.
st_args = sys.argv
len_arg = len(st_args)
pic_name, cat_division = ST_functions.review_init_data(st_args, len_arg)

# - First review.
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
first_ra_catalog = match_candidates[try_number][0]
first_dec_catalog = match_candidates[try_number][1]
first_match_data = ST_functions.get_first_match_data(match_candidates, try_number)
first_match_output_pix = ST_functions.apply_match_trans(first_match_data)
first_ra_pix = first_match_output_pix[0]
first_dec_pix = first_match_output_pix[1]
first_roll_deg = first_match_output_pix[2]
first_alpha, first_delta = ST_functions.deproject(rpi_focal, first_ra_pix, first_dec_pix,
                                                  first_ra_catalog, first_dec_catalog)

# - Second review.
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
    print '-*'*50

# 6.- With the aid of the first result, try a second 'match' to refine the pointing solution.
noproj_table = ST_functions.search_catalog_objects(DIR_normal_cat, first_ra_catalog, first_dec_catalog)

# - Third review.
if review:
    print '-*'*50
    print ' *** REVIEW - 3 *** '
    print ' --- NORMAL CATALOG COINCIDENCES --- '
    print noproj_table
    print 'TABLE LENGTH:', len(noproj_table)
    print '-*'*50
