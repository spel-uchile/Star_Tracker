# 1.- Imports
# import ST_functions
import os
import sys

# 2.- Define directories.
DIR_root = os.path.dirname(os.path.abspath(__file__)) + '/'


st_args = sys.argv
if len(st_args) == 1:
    pic_name = ' asdf '
    catalog_division = 0
    print '- Too few arguments.'
    print '- Add the full directory to the image to analyze.'
elif len(st_args) == 2:
    pic_name = sys.argv[1]
    catalog_division = 10
    print '- Using default catalog division (10 degrees).'
elif len(st_args) == 3:
    pic_name = sys.argv[2]
    catalog_division = sys.argv[1]
    print '- Catalog division: ', int(catalog_division), 'degrees.'
elif len(st_args) > 3:
    pic_name = ' asdf '
    catalog_division = 0
    print '- Too many arguments.'


#    pic_name = sys.argv[2]
# except IndexError:
#    pic_name = 'NO_NAME'
#    print '- You need to add the full directory of the image to analyze.'
#
# try:
#    catalog_division = sys.argv[1]
# except IndexError:
#    catalog_division = 10
#    print '- Using default catalog division.'

print 'ARGUMENTS:', st_args
print 'Image name:', pic_name
print 'DIR: ', DIR_root
