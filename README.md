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
  <img src="https://github.com/spel-uchile/Star_Tracker/blob/master/STT_SUCHAI2.jpg" width="460"/>
</p>
The image shows the STT payload being integrated into the SUCHAI-2 nanosatellite. The RPi Zero W is attached following 
the PC-104 standard, with the RPi V2.1 camera and the associated electronics to make it work properly.

## 2.- Description

- This GitHub contains a fully functional STT you can test on a Linux PC. Nevertheless, the main idea 
is to use it with a Raspberry Pi (RPi) and its camera (V2.1) in an autonomous way.
- This code is currently working on *Python 3.10*. All the code and the necessary files are in the **RPi** folder.
- This GitHub is **free** and **open** to everyone interested in using it, **especially researchers working on CubeSats.** 
We encourage interested researchers to help this project grow!

## 3.- Installation instructions

1. Two open software commonly used in the astronomy field are the base of this STT code: [Source Extractor](https://www.astromatic.net/software/sextractor)
and [Match](http://spiff.rit.edu/match/). To properly use this STT, you first need to install these two software. In a Linux computer, you 
can do it using the bash script provided in *RPi/linux_installer.sh*: <br />
```bash
cd RPi
sh linux_installer.sh
```
In our implementation, we use version **2.19.5** of Source Extractor and version **0.14** of Match. However, using
newer version of Source Extractor should not be a problem for the algorithm. <br />

2. For memory reasons, star catalogs are compressed (tar.gz). You can decompress it using the batch script
in *RPi/extract_cat.sh*: <br />
```bash
cd RPi
sh extract_cat.sh
```

3. This STT software uses the following *Python* libraries:
- argparse
- [astropy](http://www.astropy.org)
- itertools
- multiprocessing
- numpy
- os
- pillow
- platform
- re
- subprocess
- time

Most of them come by default in *Python*, and the remaining can be installed by typing in the terminal:
```bash
python3 -m pip install astropy pillow
```

## 4.- Use instructions

This STT software works by comparing the grabbed picture with a stellar catalog. The different catalog segments can 
be separated by 5, 10, or 15 degrees. The larger the catalog separation, the faster the algorithm works, but the 
less accurate the solution. You can choose the catalog separation when you run the code. <br />
You can test this STT software in three different ways:
- Directly grabbing pictures with the RPi and the V2.1 camera.
- Using the sample images previously grabbed with the RPi V2.1 camera.
- Using the sample images from the satellite STEREO HI-1.

### 4.1.- Taking pictures with the RPi and the V2.1 camera
The syntax is the following:
```bash
python3 stt.py direct_rpi <catalog-division>
```
Catalog division can be 5, 10 or 15. This will acquire a picture with a predefined exposure time of 800 ms. If you 
want to set your own exposure time, you can try:
```bash
python3 stt.py direct_rpi <catalog-division> -exp <exposure-time>
```
The exposure time is in **ms**.

### 4.2.- Using RPi sample images
The syntax is the following:
```bash
python3 stt.py sample_rpi <catalog-division>
```
Catalog division can be 5, 10 or 15. This will apply the algorithm over the first picture in the sample images. If you 
want to try another picture, you can try:
```bash
python3 stt.py sample_rpi <catalog-division> -n <picture-number>
```
The argument <picture-number> ranges from 1 to 50.

### 4.3.- Using [STEREO](https://stereo.gsfc.nasa.gov/) sample pictures

This STT software can also be tested with pictures from the [HI-1 detector](http://www.stereo.rl.ac.uk/) from the STEREO mission. This procedure 
proves that different cameras can be used with this algorithm, and it is not attached to particular hardware. <br />
The STEREO HI-1 pictures can have different processing levels. These levels are well explained 
in [STEREO HI data processing documentation](https://www.ukssdc.ac.uk/solar/stereo/documentation/HI_processing.html). We use two different image format:

- L0 images, which can be downloaded from [STEREO SCIENCE CENTER - L0](https://stereo-ssc.nascom.nasa.gov/pub/ins_data/secchi/L0/a/img/hi_1/).
- L2 images, which can be downloaded from [STEREO SCIENCE CENTER - L2](https://stereo-ssc.nascom.nasa.gov/pub/ins_data/secchi_hi/L2/a/img/hi_1/).

There are examples of pictures of both kinds in folder *RPi/Sample_images/STEREO* <br />
To execute the code, the syntax is the following:
```bash
python3 stt.py sample_stereo <catalog-division>
```
Like the previous cases, catalog division can be 5, 10 or 15. The attitude information can be read from the STEREO 
image header. Several programs can be used for it, for example, [DS9](https://sites.google.com/cfa.harvard.edu/saoimageds9).

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
Postdoc at SPEL group. <br />
PhD in Electrical Engineering at the University of Chile, Santiago, Chile. <br />
samuel.gutierrez@ug.uchile.cl

<br />
README updated August 29, 2024, by SGR.
