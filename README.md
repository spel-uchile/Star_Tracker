# SPEL - Open Star Tracker (SPEL - OST)

## 1.- Overview

This GitHub contains the Star Tracker (ST) development for SUCHAI 2 - 3. 
SUCHAI-1 is the first NanoSatellite developed by Universidad de Chile, at the 
Space and Planetary Exploration Laboratory (SPEL). Launched on June 23 (2017), 
the satellite is currently operational. Today we are working on two more NanoSatellites, the SUCHAI 
2 & 3. It is expected that this new satellites have attitude determination and control system (ADCS). <br />
[More info about the SUCHAI proyect.](http://spel.ing.uchile.cl)

## 2.- Description

- This is a fully functional Star Tracker that you can try on a Linux PC. Nevertheless, the main idea is to use it with a Raspberry Pi (RPI) and its camera in an autonomously way.
- This code is written in _Python 2.7_. All the code and the necessary files are in the __RPI__ folder.
- This Git-Hub is __free__ and __open__ to everyone interested in using it, __especially researchers working on CubeSats!__. 

## 3.- Installation instructions

1. This ST code is based on two open softwares commonly used in the astronomy field: __Source Extractor__ and __Match__. To use this ST you need to install these two software first.<br />
    1.1.- Get and install [Source Extractor.](https://www.astromatic.net/software/sextractor) 
You can find this program in the Linux (RPI) repository, and install it by typing in the terminal: <br />
_~$ sudo apt-get install sextractor_ <br />
We use __version 2.19.5__ in our program. <br />
    1.2.- Get and install [Match](http://spiff.rit.edu/match/). We use __version 0.14__ in our program.
2. This ST program uses the [Astropy](http://www.astropy.org) package. You can install it by typing in the terminal: <br />
_~$ pip install astropy_
3. Finally, clone this repository in any folder on your RPI, for example: __/home/pi/Desktop/Git/ST/__

## 4.- Instructions for use

This ST program works by comparing the acquired photo with a stellar catalog. The different catalog segments can be separated by 5 or 10 degrees, you can choose it when you run the program. You can test this ST program with RPI pictures or with STEREO HI-1 pictures.

### 4.1.- To use it with Raspberry Pi pictures

1. For a 10 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_10_deg.py_ <br />
By default, it will use a picture from __/RPI/Sample_images/__. You can test it with other pictures on the same folder, or use your own pictures taken with a RPI camera.
2. For a 5 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_5_deg.py_

### 4.2.- To use it with [STEREO](https://stereo.gsfc.nasa.gov/) pictures

This ST program can also be tested with pictures from the [HI-1 detector](http://www.stereo.rl.ac.uk/) from STEREO mission. You can use pictures from the folder __/RPI/STEREO_pics/__ or download any HI-1 photo from [SECCHI Flight Images Database](https://secchi.nrl.navy.mil/cgi-bin/swdbi/secchi_flight/images/form).<br />
1. For a 10 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_10_deg_FITS.py < full path to HI-1 picture >_ <br />
2. For a 5 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_5_deg_FITS.py < full path to HI-1 picture >_

## 5.- Any questions?

Contact: Samuel Gutiérrez Russell. <br />
PhD student in Electrical Engineering at Universidad de Chile, Santiago, Chile. <br />
e-mail: samuel.gutierrez@ug.uchile.cl

<br />
README updated September 4, 2018 by SGR.
