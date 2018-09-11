# 1.- Imports
import time
import os
import re
import subprocess
import multiprocessing
import commands
import numpy as np
from PIL import Image
from astropy.io import fits, ascii
from astropy.table import Table


# Check the initial data entered to the code.
def rev_initial_data(sys_arg, len_arg):
    if len_arg == 1:
        print '- Too few arguments...'
        print '- Add the full directory of the image.'
        raise ValueError('Invalid data...')
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
def generate_fits(pic_name, fits_name):
    image = Image.open(pic_name)
    imagebw = image.convert('L')
    xsize, ysize = imagebw.size
    fits1 = imagebw.getdata()
    fits2 = np.array(fits1)
    fits3 = fits2.reshape(ysize, xsize)
    fits4 = np.flipud(fits3)
    fits5 = fits.PrimaryHDU(data=fits4)
    fits5.writeto(fits_name, overwrite=True)
    return
