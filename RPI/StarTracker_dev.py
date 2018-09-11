# 1.- Imports.
import ST_functions
import sys

# 2.- Define directories, names and important values.
DIRs = ST_functions.names_and_dir()
values = ST_functions.st_constants()

# 3.- Receives and reviews the initial data.
st_args = sys.argv
len_arg = len(st_args)
pic_name, cat_division = ST_functions.rev_initial_data(st_args, len_arg)

print '-.'*30
print 'REVIEW - 1:'
print 'Initial arguments:', st_args
print 'Image name:', pic_name
print 'DIR_this: ', DIRs[0]
print '-.'*30

# 4.- Generate FITS image and execute SExtractor.
ST_functions.generate_fits(pic_name, DIRs[7])
ST_functions.apply_sext(DIRs[4], DIRs[1], DIRs[7], values[0], values[1], values[2])
