# 1.- Imports.
import ST_functions
import sys

# 2.- Define directories, names and constants values.
DIRs = ST_functions.names_and_dir()
DIR_this = DIRs[0]
DIR_img_fits = DIRs[1]
DIR_sext = DIRs[4]
fits_name = DIRs[7]
const = ST_functions.st_constants()
x_pix = const[0]
y_pix = const[1]
cmos2pix = const[2]

# 3.- Receives and reviews the initial data.
st_args = sys.argv
len_arg = len(st_args)
pic_name, cat_division = ST_functions.rev_initial_data(st_args, len_arg)

print '-.'*30
print 'REVIEW - 1:'
print 'Initial arguments:', st_args
print 'Image name:', pic_name
print 'DIR_this: ', DIR_this
print '-.'*30

# 4.- Generate FITS image and execute SExtractor.
ST_functions.generate_fits(pic_name, fits_name)
ST_functions.apply_sext(DIR_sext, DIR_img_fits, fits_name, x_pix, y_pix, cmos2pix)
