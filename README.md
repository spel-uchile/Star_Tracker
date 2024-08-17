# SPEL - Open Star Tracker (SOST)

## 1.- Overview

This GitHub offers to the CubeSat research community an open-source Star Tracker (STT), 
developed at the Space and Planetary Exploration Laboratory (SPEL) at the University of Chile. 
We used this development in the first Chilean satellite swarm made up of SUCHAI-2/3 and PlantSAT. <br/>
SUCHAI-1 was the first NanoSatellite developed by the University of Chile at SPEL. Launched on June 23 (2017), this satellite 
worked 457 days on space. On April 1, 2022, the second batch of satellites was launched: the SUCHAI-2/3 and PlantSAT.
We tested the pointing capabilities of these new satellites and learned how to develop a robust attitude
determination and control system (ADCS) through in-house sensors and algorithms development. <br/>
---> Links of interest:
- [SUCHAI-1](http://ingenieria.uchile.cl/noticias/144476/suchai-ha-dado-mas-de-5-mil-vueltas-a-la-tierra-en-su-primer-ano) <br/>
- [The SUCHAI project](http://spel.ing.uchile.cl) <br/>
- [PlantSAT project](https://plantsat.spel.cl/) <br/>
- [SPEL](https://spel.cl/) <br/>
- [The first chilean satellite swarm in the SmallSat Conference (2023)](https://digitalcommons.usu.edu/smallsat/2023/all2023/56/) <br/>
- [SOST paper in IEEE ACCESS (2020)](https://ieeexplore.ieee.org/document/9179736) <br/>

<p align="center">
  <img src="https://github.com/spel-uchile/Star_Tracker/blob/master/stt.jpg" width="460"/>
</p>

## 2.- Description

- This GitHub contains a fully functional Star Tracker that you can test on a Linux PC. 
Nevertheless, the main idea is to use it with a Raspberry Pi (RPi) and its camera (V2.1) in an autonomous way.
- This code is written in _Python 2.7_. All the code and the necessary files are in the __RPi__ folder.
- This GitHub is __free__ and __open__ to everyone interested in using it, __especially researchers working on CubeSats.__ 
We encourage interested researchers to aid in growing up this project!

## 3.- Installation instructions

1. Two open software commonly used in the astronomy field are the base of this STT code: [Source Extractor](https://www.astromatic.net/software/sextractor)
and [Match](http://spiff.rit.edu/match/). To properly use this STT, you first need to install these two software. You can do it using the
bash script provided in *RPi/stt_installer.sh*: <br />
```bash
cd RPi
sh stt_installer.sh
```
In our implementation, we use version **2.19.5** of Source Extractor and version **0.14** of Match. However, using
newer version of Source Extractor should not be a problem for the algorithm. <br />

2. This STT software uses the [Python-Astropy](http://www.astropy.org) package. You can install it by typing in the terminal:
```bash
python3 -m pip install astropy
```

## 4.- Use instructions

This STT software works by comparing the acquired picture with a stellar catalog. The different catalog segments can be separated by 5, 10, or 15 degrees.
You can choose it when you run the program. You can test this STT program with RPi pictures or with STEREO HI-1 pictures.

### 4.1.- To use it with Raspberry Pi pictures

By default, this software will use a picture from __/RPI/Sample_images/__. You can test it with other pictures on the same folder, or use your pictures taken with a Raspberry Pi V2.1 camera. <br />
1. For a 10 degrees catalog separation, run in the terminal: <br />
```bash
python StarTracker_10_deg.py
```
2. For a 5 degrees catalog separation, run in the terminal: <br />
```bash
python StarTracker_5_deg.py
```

### 4.2.- To use it with [STEREO](https://stereo.gsfc.nasa.gov/) pictures

This STT software can also be tested with pictures from the [HI-1 detector](http://www.stereo.rl.ac.uk/) from the STEREO mission. This procedure proves that different cameras can be used with this algorithm, and it is not attached to particular hardware. <br />
The STEREO HI-1 pictures can have different processing levels. These levels are well explained in [STEREO HI data processing documentation](https://www.ukssdc.ac.uk/solar/stereo/documentation/HI_processing.html). We use two different image format:

- L0 images, which can be downloaded from [STEREO SCIENCE CENTER - L0](https://stereo-ssc.nascom.nasa.gov/pub/ins_data/secchi/L0/a/img/hi_1/).
- L2 images, which can be downloaded from [STEREO SCIENCE CENTER - L2](https://stereo-ssc.nascom.nasa.gov/pub/ins_data/secchi_hi/L2/a/img/hi_1/).

There are examples of pictures of both kinds in folder __/RPI/STEREO_pics/__. <br />
1. For a 10 degrees catalog separation, run in the terminal:
```bash
python StarTracker_10_deg_FITS.py <full_path_to_HI-1_picture>
```
2. For a 5 degrees catalog separation, run in the terminal:
```bash
python StarTracker_5_deg_FITS.py <full_path_to_HI-1_picture>
```

The attitude information can be read from the STEREO image header. Various software can be used for it, for example, [DS9](https://sites.google.com/cfa.harvard.edu/saoimageds9).

## 5.- Research

This STT is deeply tested with theoretical analysis and ground-based night-sky pictures. 
The tools, algorithms, methods, and results are fully described in my paper in IEEE ACCESS.
If you are using this open project in your research or development, please cite it using the following BibTeX:
```bibtex
@article{gutierrez2020introducing,
  title     = {Introducing SOST: An Ultra-Low-Cost Star Tracker Concept Based on a Raspberry Pi and Open-Source Astronomy Software},
  author    = {Guti{\'e}rrez, Samuel T and Fuentes, C{\'e}sar I and D{\'\i}az, Marcos A},
  journal   = {IEEE Access},
  volume    = {8},
  pages     = {166320--166334},
  year      = {2020},
  publisher = {IEEE}
}
```

## 6.- Any questions?

Contact: Samuel T. Gutiérrez. <br />
PhD in Electrical Engineering at the University of Chile, Santiago, Chile. <br />
e-mail: samuel.gutierrez@ug.uchile.cl

<br />
README updated August 17, 2024, by SGR.
