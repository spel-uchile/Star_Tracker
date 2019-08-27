# SPEL - Open Star Tracker (SOST)

## 1.- Overview

This GitHub contains the Star Tracker (STT) development for the followings SUCHAI 2 & 3. 
SUCHAI-1 was the first NanoSatellite developed by Universidad de Chile, at Space and Planetary Exploration Laboratory (SPEL). Launched on June 23 (2017), 
this satellite worked 457 days on space. Today in SPEL we are working on three new NanoSatellites, the SUCHAI 2 & 3 and PlantSat. 
It is expected that these new satellites have pointing capabilities, with a robust attitude determination and control system (ADCS). <br />
-> More info about the [SUCHAI project](http://spel.ing.uchile.cl) and [PlantSat](https://plantsat.spel.cl/).

## 2.- Description

- This is a fully functional Star Tracker that you can test on a Linux PC. Nevertheless, the main idea is to use it with a Raspberry Pi (RPI) and its camera in an autonomously way.
- This code is written in _Python 2.7_. All the code and the necessary files are in the __RPI__ folder.
- This GitHub is __free__ and __open__ to everyone interested in using it, __especially researchers working on CubeSats.__ We encourage interested 
researchers to aid in growing up this project!

## 3.- Installation instructions

1. This STT code is based on two open software commonly used in the astronomy field: __Source Extractor__ and __Match__. To use this STT you need to install first this two software.<br />
    1.1.- Get and install [Source Extractor.](https://www.astromatic.net/software/sextractor) 
You can find this program in the Linux (RPI) repository, and install it by typing in the terminal: <br />
_~$ sudo apt-get install sextractor_ <br />
We use __version 2.19.5__ in our program. <br />
    1.2.- Get and install [Match](http://spiff.rit.edu/match/). We use __version 0.14__ in our program.
2. This STT software uses the [Python-Astropy](http://www.astropy.org) package. You can install it by typing in the terminal: <br />
_~$ pip install astropy_
3. Finally, clone this repository in any folder on your RPI, for example: __/home/pi/Desktop/Git/ST/__

## 4.- Instructions for use

This STT software works by comparing the acquired photo with a stellar catalog. The different catalog segments can be separated by 5, 10 or 15 degrees. 
You can choose it when you run the program. You can test this STT program with RPI pictures or with STEREO HI-1 pictures.

### 4.1.- To use it with Raspberry Pi pictures

1. For a 10 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_10_deg.py_ <br />
By default, it will use a picture from __/RPI/Sample_images/__. You can test it with other pictures on the same folder, or use your own pictures taken with a Raspberry Pi camera.
2. For a 5 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_5_deg.py_

### 4.2.- To use it with [STEREO](https://stereo.gsfc.nasa.gov/) pictures

This STT software can also be tested with pictures from the [HI-1 detector](http://www.stereo.rl.ac.uk/) from STEREO mission. You can use pictures from the folder __/RPI/STEREO_pics/__ or download any HI-1 photo from [SECCHI Flight Images Database](https://secchi.nrl.navy.mil/cgi-bin/swdbi/secchi_flight/images/form).<br />
1. For a 10 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_10_deg_FITS.py < full path to HI-1 picture >_ <br />
2. For a 5 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_5_deg_FITS.py < full path to HI-1 picture >_

## 5.- Any questions?

Contact: Samuel Gutiérrez Russell. <br />
Ph.D. student in Electrical Engineering at Universidad de Chile, Santiago, Chile. <br />
e-mail: samuel.gutierrez@ug.uchile.cl

<br />
README updated August 27, 2019, by SGR.
