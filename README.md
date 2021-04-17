# SPEL - Open Star Tracker (SOST)

## 1.- Overview

This GitHub offers to the CubeSat research community an open-source Star Tracker (STT), developed at the Space and Planetary Exploration Laboratory (SPEL) at the University of Chile. We will use this development in our following satellites. <br/>
[SUCHAI-1](http://ingenieria.uchile.cl/noticias/144476/suchai-ha-dado-mas-de-5-mil-vueltas-a-la-tierra-en-su-primer-ano) was the first NanoSatellite developed by the University of Chile at SPEL. Launched on June 23 (2017), this satellite worked 457 days on space. Today in SPEL, we are working on three new NanoSatellites, the SUCHAI 2 & 3 and PlantSat.
These new satellites will have pointing capabilities, with a robust attitude determination and control system (ADCS). <br/>
--> More info about the [SUCHAI project](http://spel.ing.uchile.cl) and [PlantSat](https://plantsat.spel.cl/).

<!---
![alt text](https://github.com/spel-uchile/Star_Tracker/blob/master/stt.jpg?raw=true)
-->
<img src="https://github.com/spel-uchile/Star_Tracker/blob/master/stt.jpg" width="400"/>

## 2.- Description

- This GitHub contains a fully functional Star Tracker that you can test on a Linux PC. Nevertheless, the main idea is to use it with a Raspberry Pi (RPi) and its camera (V2.1) in an autonomously way.
- This code is written in _Python 2.7_. All the code and the necessary files are in the __RPI__ folder.
- This GitHub is __free__ and __open__ to everyone interested in using it, __especially researchers working on CubeSats.__ We encourage interested 
researchers to aid in growing up this project!

## 3.- Installation instructions

1. Two open software commonly used in the astronomy field: __Source Extractor__ and __Match__, are the base of this STT code. To use this STT, you need to install first these two software.<br />
    1.1.- Get and install [Source Extractor.](https://www.astromatic.net/software/sextractor)
You can find this program in the Linux (RPI) repository, and install it by typing in the terminal: <br />
_~$ sudo apt-get install sextractor_ <br />
We use __version 2.19.5__ in our program. <br />
    1.2.- Get and install [Match](http://spiff.rit.edu/match/). We use __version 0.14__ in our program.
2. This STT software uses the [Python-Astropy](http://www.astropy.org) package. You can install it by typing in the terminal: <br />
_~$ pip install astropy_
3. Finally, clone this repository in any folder on your RPI, for example: __/home/pi/Desktop/Git/ST/__

## 4.- Instructions for use

This STT software works by comparing the acquired picture with a stellar catalog. The different catalog segments can be separated by 5, 10, or 15 degrees.
You can choose it when you run the program. You can test this STT program with RPi pictures or with STEREO HI-1 pictures.

### 4.1.- To use it with Raspberry Pi pictures

By default, this software will use a picture from __/RPI/Sample_images/__. You can test it with other pictures on the same folder, or use your pictures taken with a Raspberry Pi V2.1 camera. <br />
1. For a 10 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_10_deg.py_ <br />
2. For a 5 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_5_deg.py_

### 4.2.- To use it with [STEREO](https://stereo.gsfc.nasa.gov/) pictures

This STT software can also be tested with pictures from the [HI-1 detector](http://www.stereo.rl.ac.uk/) from the STEREO mission. This procedure proves that different cameras can be used with this algorithm, and it is not attached to particular hardware. <br />
The STEREO HI-1 pictures can have different processing levels. These levels are well explained in [STEREO HI data processing documentation](https://www.ukssdc.ac.uk/solar/stereo/documentation/HI_processing.html). We use two different image format:

- L0 images, which can be download from [STEREO SCIENCE CENTER - L0](https://stereo-ssc.nascom.nasa.gov/pub/ins_data/secchi/L0/a/img/hi_1/).
- L2 images, which can be download from [STEREO SCIENCE CENTER - L2](https://stereo-ssc.nascom.nasa.gov/pub/ins_data/secchi_hi/L2/a/img/hi_1/).

There are examples of pictures of both kinds in folder __/RPI/STEREO_pics/__. <br />
1. For a 10 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_10_deg_FITS.py_ < full path to HI-1 picture > <br />
2. For a 5 degrees catalog separation, run in the terminal: <br />
_~$ python StarTracker_5_deg_FITS.py_ < full path to HI-1 picture >

The attitude information can be read from the STEREO image header, and various software can be used for it, for example, [DS9](https://sites.google.com/cfa.harvard.edu/saoimageds9).

## 5.- Any questions?

Contact: Samuel T. Gutiérrez. <br />
Ph.D. student in Electrical Engineering at the University of Chile, Santiago, Chile. <br />
e-mail: samuel.gutierrez@ug.uchile.cl

<br />
README updated April 17, 2021, by SGR.
