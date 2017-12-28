# Star Tracker

This GitHub contains the Star Tracker (ST) development for SUCHAI 2 - 3. <br />
SUCHAI 1 is the first NanoSatellite developed by Universidad de Chile, at the 
Space and Planetary Exploration Laboratory (SPEL). Launched on June 23 (2017), the satellite is currently operational. <br />
Actually, we are working in two more NanoSats, the SUCHAI 2 & 3. [More info about the SUCHAI proyect](http://spel.ing.uchile.cl).

## Description

- This is a fully functional Star Tracker for use with a Raspberry Pi and its camera. <br />
- This code is written in _Python_. All the code and the necessary files are in the __RPI__ folder. <br />
- This Git-Hub is free and open to everyone interested in using it, __especially researchers working on CubeSats!__. <br />

## Instructions for use

1. This ST code is based on two open softwares: __Source Extractor__ and __Match__. In order to use it, you need this two software first.<br />
    1.1. Get [Source Extractor](https://www.astromatic.net/software/sextractor). <br />
    1.2. Get [Match](http://spiff.rit.edu/match/). We use __version 0.14__ in our _Python_ program. <br />
    1.3. Install this two programs in your RPI. <br />

2. Clone this repository in any folder on your RPI, for example: __/home/pi/Desktop/ST/__

3. Run in _Python_ the file _StarTracker_10deg.py_. By default, it will use a picture from __RPI/Sample_Images/__. You can test with other pictures, or use your own taked with the RPI Camera.

## Any questions?

Contact: Samuel Gutiérrez Russell. <br />
PhD student in Electrical Engineering at Universidad de Chile, Santiago, Chile. <br />

e-mail: samuel.gutierrez@ug.uchile.cl
