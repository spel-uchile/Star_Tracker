# 1.- Imports.
import ST_functions
import os
import sys

# 2.- Define directories and names.
DIR_this = os.path.dirname(os.path.abspath(__file__)) + '/'
DIR_img_fits = DIR_this
DIR_stars = DIR_img_fits + 'sext'
DIR_first_match = DIR_img_fits + 'new_cat'
DIR_sext = './sextractor'
DIR_proj_cat = './Catalog/Projected/'
DIR_normal_cat = './Catalog/Normal/'
fits_name = 'img_fits.fits'

# 3.- Receives initial data.
st_args = sys.argv
len_arg = len(st_args)
pic_name, cat_division = ST_functions.rev_initial_data(st_args, len_arg)

print '-.'*20
print 'REVIEW:'
print 'Initial arguments:', st_args
print 'Image name:', pic_name
print 'DIR_this: ', DIR_this
print '-.'*20

# 4.- Generate FITS image.
ST_functions.generate_fits(pic_name, fits_name)
