# 1.- Import libraries.
import sys
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


pic_name = sys.argv[1]
# Get current directory.
Cur_Dir = os.path.dirname(os.path.abspath(__file__)) + '/'

# Img .jpg name.
#img_jpg_name = 'img.jpg'
nombre_img_jpg = pic_name
# Directorio imagen .jpg.
dir_img_jpg = nombre_img_jpg
# Directorio donde se guarda imagen .fits.
dir_img_fits = Cur_Dir
# Nombre imagen .fits.
nombre_img_fits = 'img_fits.fits'
# Directorio SExtractor.
dir_sext = './sextractor'
# Directorio base del catalogo proyectado.
path_base = './Catalog/Projected/'
# Directorio donde se guarda el archivo 'sext'.
path_stars = dir_img_fits + 'sext'
# Directorio base de catalogo no proyectado.
cat_no_proy = './Catalog/Normal/'
# Directorio donde se guarda el catalogo proyectado en el punto que entrega como resultado el primer Match.
new_path_catalog = dir_img_fits + 'new_cat'

## 4.- Transformacion imagen a .fits.

# Lectura de imagen.
image = Image.open(dir_img_jpg)
# Conversion a escala de grises.
imagebn = image.convert('L')
# Obtiene el tamano de la imagen.
xsize, ysize = imagebn.size
# Toma los datos de cuentas de la imagen (0 - 255).
fits_aux1 = imagebn.getdata()
# Guarda esas cuentas en un arreglo.
fits_aux2 = np.array(fits_aux1)
# Transforma ese arreglo a las mismas dimensiones de la imagen.
fits_aux3 = fits_aux2.reshape(ysize, xsize)
# Invierte el array para quedar en la orientacion adecuada.
fits_aux4 = np.flipud(fits_aux3)
# Crea un archivo .fits basico.
fits_aux5 = fits.PrimaryHDU(data=fits_aux4)
# Guarda el archivo en formato "fits".
fits_aux5.writeto(nombre_img_fits, clobber=True)

## 5.- Ejecuta SExtractor.

# Cambia el directorio al de SExtractor.
os.chdir(dir_sext)
# Define el directorio de la imagen.
imdir = dir_img_fits + nombre_img_fits
# Define el sextractor.
sext = 'sextractor ' + imdir
# Se corre sextractor. Genera "test.cat" y se lee como tabla.
subprocess.check_output(sext, shell=True)
sex_aux1 = ascii.read('./test.cat', format='sextractor')
# Ordena por magnitud y selecciona las 40 estrellas mas brillantes.
sex_aux1.sort(['MAG_ISO'])
sex_aux2 = sex_aux1[0:40]
# Cambia el directorio.
os.chdir(dir_img_fits)
## Define posiciones X e Y a partir de los datos entregados por SExtractor.
sex_x = sex_aux2['X_IMAGE']
sex_y = sex_aux2['Y_IMAGE']
sex_mag = sex_aux2['MAG_ISO']
# Conversion a coordenadas de CMOS.
sex_x1 = (sex_x - 512)*0.00270   # queda en mm centrada en (0,0)
sex_y1 = (sex_y - 512)*0.00270   # queda en mm centrada en (0,0)
# Guarda las columnas X, Y y MAG del resultado de Sextractor.
ascii.write([sex_x1, sex_y1, sex_mag], 'sext', delimiter = ' ', format = 'no_header', formats = {'col0':'% 15.10f', 'col1':'% 15.10f', 'col2':'% 15.10f'})

## 6.- Match: First iteration.

time4 = time.time()
# Define regular expresion for Match.
match_reg = re.compile(r"a=(-*\d\.\d+e...) b=(-*\d\.\d+e...) c=(-*\d\.\d+e...) d=(-*\d\.\d+e...) e=(-*\d\.\d+e...) f=(-*\d\.\d+e...) sig=(-*\d\.\d+e...) Nr=(-*\d+) Nm=(-*\d+) sx=(-*\d\.\d+e...) sy=(-*\d\.\d+e...) ")
# Definimos el path para el catalogo.
path_catalog1 = path_base + 'cat_RA_'
# Definimos parametros de 'match'.
parametros1 = 'trirad=0.002 nobj=15 max_iter=1 matchrad=1 scale=1'
# Inicializamos una tabla.
match1_tabla1 = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))

def call_match(ra_dec):
    RA1, DEC1 = ra_dec
    # Transform RA and DEC in string and make the path for catalog.
    path_catalog2 = str(RA1) + '_DEC_' + str(DEC1)
    path_catalog3 = path_catalog1 + path_catalog2
    # Do Match.
    Match1 = 'match ' + path_stars + ' 0 1 2 ' + path_catalog3 + ' 0 1 2 ' + parametros1
    status1, resultado1 = commands.getstatusoutput(Match1)
    return status1, resultado1

# Create the list of parameters.
ra_dec = [(ra, dec) for ra in range(0, 360, 10) for dec in range(-80, 90, 10)]

pool = multiprocessing.Pool(2)
results = pool.map(call_match, ra_dec)

for i, (status1, resultado1) in enumerate(results):
    RA1, DEC1 = ra_dec[i]
    if status1 == 0:
        # Busqueda de resultados estadisticos.
        match1_aux1 = resultado1.find('sig=')
        match1_aux2 = resultado1.find('Nr=')
        match1_auxsig1 = resultado1[match1_aux1+4:match1_aux1+25]
        match1_auxnr1 = resultado1[match1_aux2+3:match1_aux2+10]
        match1_sig1 = match1_auxsig1.split(' ', 1)[0]
        match1_nr1 = match1_auxnr1.split(' ', 1)[0]
        match1_tabla1.add_row([str(RA1), str(DEC1), match1_sig1, match1_nr1])

#Ciclo de busqueda para RA = 0 y DEC = +- 90 deg.
RA2 = 0
for j in range (-90, 100, 180):
    # Define intervalo de DEC (en -90 deg y 90 deg).
    DEC2 = j
    # Transforma en string RA y DEC y arma el path del catalogo.
    path_catalog4 = str(RA2) + '_DEC_' + str(DEC2)
    path_catalog5 = path_catalog1 + path_catalog4
    # Se hace match.
    Match2 = 'match ' + path_stars + ' 0 1 2 ' + path_catalog5 + ' 0 1 2 ' + parametros1
    status2, resultado2 = commands.getstatusoutput(Match2)
    # Si hay 'match' se analizan sus resultados.
    if status2 == 0:
        # Busqueda de resultados estadisticos.
        match1_aux3 = resultado2.find('sig=')
        match1_aux4 = resultado2.find('Nr=')
        match1_auxsig2 = resultado2[match1_aux3+4:match1_aux3+25]
        match1_auxnr2 = resultado2[match1_aux4+3:match1_aux4+10]
        match1_sig2 = match1_auxsig2.split(' ', 1)[0]
        match1_nr2 = match1_auxnr2.split(' ', 1)[0]
        match1_tabla1.add_row([str(RA2), str(DEC2), match1_sig2, match1_nr2])
if len(match1_tabla1) == 0:
    print 'No hay match'
else:
    ## Reordena la tabla por menor 'Nr'.
    match1_tabla1.sort('Nr')
    match1_tabla1.reverse()
    # Seleccion del resultado correcto.
    if len(match1_tabla1) >= 3:
        a = match1_tabla1[0]['sig']
        b = match1_tabla1[1]['sig']
        c = match1_tabla1[2]['sig']
        if a <= b:
            if a <= c:
                i = 0
            else:
                i = 2
        else:
            if b <= c:
                i = 1
            else:
                i = 2
    if len(match1_tabla1) == 2:
        a = match1_tabla1[0]['sig']
        b = match1_tabla1[1]['sig']
        if a <= b:
            i = 0
        else:
            i = 1
    if len(match1_tabla1) == 1:
        i = 0
    ## Repite el match optimo para encontrar la relacion de transformacion.
    # Transforma en string RA y DEC.
    match1_RA = int(match1_tabla1[i][0])
    match1_DEC = int(match1_tabla1[i][1])
    path_catalog6 = str(match1_RA) + '_DEC_' + str(match1_DEC)
    # Arma el path del catalogo.
    path_catalog7 = path_catalog1 + path_catalog6
    # Se hace match.
    Match3 = 'match ' + path_stars + ' 0 1 2 ' + path_catalog7 + ' 0 1 2 ' + parametros1
    # Prueba Match.
    resultado3 = subprocess.check_output(Match3, shell=True)
    #Busqueda de parametros.
    match1_aux5 = resultado3.find('a=')
    match1_aux6 = resultado3.find('b=')
    match1_aux7 = resultado3.find('c=')
    match1_aux8 = resultado3.find('d=')
    match1_aux9 = resultado3.find('e=')
    match1_aux10 = resultado3.find('f=')
    match1_aux11 = resultado3.find('sig=')
    match1_aux12 = resultado3.find('Nr=')
    match1_aux13 = resultado3.find('Nm=')
    match1_auxa1 = resultado3[match1_aux5+2:match1_aux5+25]
    match1_auxb1 = resultado3[match1_aux6+2:match1_aux6+25]
    match1_auxc1 = resultado3[match1_aux7+2:match1_aux7+25]
    match1_auxd1 = resultado3[match1_aux8+2:match1_aux8+25]
    match1_auxe1 = resultado3[match1_aux9+2:match1_aux9+25]
    match1_auxf1 = resultado3[match1_aux10+2:match1_aux10+25]
    match1_auxsig3 = resultado3[match1_aux11+4:match1_aux11+25]
    match1_auxnr3 = resultado3[match1_aux12+3:match1_aux12+10]
    match1_auxnm3 = resultado3[match1_aux13+3:match1_aux13+10]
    match1_sig3 = match1_auxsig3.split(' ', 1)[0]
    match1_nr3 = match1_auxnr3.split(' ', 1)[0]
    match1_nm3 = match1_auxnm3.split(' ', 1)[0]
    match1_auxa2 = match1_auxa1.split(' ', 1)[0]
    match1_auxb2 = match1_auxb1.split(' ', 1)[0]
    match1_auxc2 = match1_auxc1.split(' ', 1)[0]
    match1_auxd2 = match1_auxd1.split(' ', 1)[0]
    match1_auxe2 = match1_auxe1.split(' ', 1)[0]
    match1_auxf2 = match1_auxf1.split(' ', 1)[0]
    match1_a = float(match1_auxa2)
    match1_b = float(match1_auxb2)
    match1_c = float(match1_auxc2)
    match1_d = float(match1_auxd2)
    match1_e = float(match1_auxe2)
    match1_f = float(match1_auxf2)
    ## Busqueda de coordenadas RA/DEC del lugar del centro y 'roll'.
    # Traslacion y rotacion de la transformacion.
    match1_T = np.array([(match1_a), (match1_d)])
    match1_R = np.array([(match1_b, match1_c), (match1_e, match1_f)])
    # Coordenadas de centro de foto en pixeles.
    match1_x_pix = 0
    match1_y_pix = 0
    match1_X_pix = np.array([(match1_x_pix), (match1_y_pix)])
    match1_X_cielo = match1_T + np.dot(match1_R, match1_X_pix)
    match1_RA_new = match1_X_cielo[0]
    match1_DEC_new = match1_X_cielo[1]
    # Calculo de angulo de 'roll'.
    match1_roll_r = np.arctan2(match1_c, match1_b)
    match1_roll_d = (180/np.pi)*match1_roll_r

## 7.- Deproyeccion del punto (0, 0) de la camara.

f = 3.04 #mm
dep1_xi = match1_RA_new/f
dep1_eta = match1_DEC_new/f
dep1_RA_r = match1_RA*(np.pi/180)
dep1_DEC_r = match1_DEC*(np.pi/180)
dep1_arg1 = np.cos(dep1_DEC_r) - dep1_eta*np.sin(dep1_DEC_r)
dep1_arg2 = np.arctan(dep1_xi/dep1_arg1)
dep1_alpha1 = match1_RA + (180/np.pi)*dep1_arg2
dep1_arg3 = np.sin(dep1_arg2)
dep1_arg4 = dep1_eta*np.cos(dep1_DEC_r) + np.sin(dep1_DEC_r)
dep1_delta1 = (180/np.pi)*np.arctan((dep1_arg3*dep1_arg4)/dep1_xi)

# Lectura de catalogo NO PROYECTADO que encontro match.
new_cat1 = cat_no_proy + 'cat_RA_' + str(match1_RA) + '_DEC_' + str(match1_DEC)
new_cat2 = ascii.read(new_cat1)
# Lectura de ambos archivos de match para buscar numero de inicio.
np_matched_B1 = ascii.read('./matched.mtB')
np_matched_B2 = ascii.read('./matched.unB')
np_aux1 = np_matched_B1[0][0]
np_aux2 = np_matched_B2[0][0]
# Define el menor numero como el contador de inicio para la busqueda.
if np_aux1>np_aux2:
    np_cont1 = np_aux2
else:
    np_cont1 = np_aux1
# Crea nueva tabla con las estrellas que hizo match.
np_tabla1 = Table([[], [], []])
# Busqueda de estrellas para agregar a tabla.
for i in range(0, len(np_matched_B1), 1):
    np_cont2 = np_matched_B1[i][0] - np_cont1
    np_tabla1.add_row([new_cat2[np_cont2][0], new_cat2[np_cont2][1], new_cat2[np_cont2][2]])


# Iniciamos arrays vacios.
cat_tran1 = Table([[], [], []])
conv1_largo1 = len(np_tabla1)
# Ciclo donde crea el arreglo de datos transformados.
for index in range (0, conv1_largo1):
    conv1_alpha_d = np_tabla1[index][0]
    conv1_delta_d = np_tabla1[index][1]
    conv1_mag = np_tabla1[index][2]
    # Conversion de grados a radianes.
    conv1_alpha_r = (np.pi/180)*conv1_alpha_d
    conv1_delta_r = (np.pi/180)*conv1_delta_d
    conv1_alpha_0_r = (np.pi/180)*dep1_alpha1
    conv1_delta_0_r = (np.pi/180)*dep1_delta1
    # Calculo de Xi (analogo a RA).
    conv1_xi_up = np.cos(conv1_delta_r)*np.sin(conv1_alpha_r - conv1_alpha_0_r)
    conv1_xi_down = np.sin(conv1_delta_0_r)*np.sin(conv1_delta_r) + np.cos(conv1_delta_0_r)*np.cos(conv1_delta_r)*np.cos(conv1_alpha_r - conv1_alpha_0_r)
    conv1_xi = conv1_xi_up/conv1_xi_down
    # Calculo de Eta (analogo a DEC).
    conv1_eta_up = np.cos(conv1_delta_0_r)*np.sin(conv1_delta_r) - np.sin(conv1_delta_0_r)*np.cos(conv1_delta_r)*np.cos(conv1_alpha_r - conv1_alpha_0_r)
    conv1_eta_down = conv1_xi_down
    conv1_eta = conv1_eta_up/conv1_eta_down
    # Conversion a mm.
    conv1_xi_mm = f*conv1_xi
    conv1_eta_mm = f*conv1_eta
    # Agrega el dato al arreglo.
    cat_tran1.add_row([conv1_xi_mm, conv1_eta_mm, conv1_mag])
# Guarda el nuevo catalogo.
ascii.write(cat_tran1, 'new_cat', delimiter = ' ', format = 'no_header', formats = {'col0':'% 15.5f', 'col1':'% 15.5f', 'col2':'% 15.2f'})

## 10.- Se hace el nuevo match (Segunda iteracion).

new_parametros1 = 'trirad=0.002 nobj=20 max_iter=3 matchrad=1 scale=1'
Match4 = 'match ' + path_stars + ' 0 1 2 ' + new_path_catalog + ' 0 1 2 ' + new_parametros1
resultado4 = subprocess.check_output(Match4, shell=True)
#Busqueda de parametros.
match2_aux1 = resultado4.find('a=')
match2_aux2 = resultado4.find('b=')
match2_aux3 = resultado4.find('c=')
match2_aux4 = resultado4.find('d=')
match2_aux5 = resultado4.find('e=')
match2_aux6 = resultado4.find('f=')
match2_aux7 = resultado4.find('sig=')
match2_aux8 = resultado4.find('Nr=')
match2_auxa1 = resultado4[match2_aux1+2:match2_aux1+25]
match2_auxb1 = resultado4[match2_aux2+2:match2_aux2+25]
match2_auxc1 = resultado4[match2_aux3+2:match2_aux3+25]
match2_auxd1 = resultado4[match2_aux4+2:match2_aux4+25]
match2_auxe1 = resultado4[match2_aux5+2:match2_aux5+25]
match2_auxf1 = resultado4[match2_aux6+2:match2_aux6+25]
match2_auxsig4 = resultado4[match2_aux7+4:match2_aux7+25]
match2_auxnr4 = resultado4[match2_aux8+3:match2_aux8+10]
match2_auxa2 = match2_auxa1.split(' ', 1)[0]
match2_auxb2 = match2_auxb1.split(' ', 1)[0]
match2_auxc2 = match2_auxc1.split(' ', 1)[0]
match2_auxd2 = match2_auxd1.split(' ', 1)[0]
match2_auxe2 = match2_auxe1.split(' ', 1)[0]
match2_auxf2 = match2_auxf1.split(' ', 1)[0]
match2_sig = match2_auxsig4.split(' ', 1)[0]
match2_nr = match2_auxnr4.split(' ', 1)[0]
match2_a = float(match2_auxa2)
match2_b = float(match2_auxb2)
match2_c = float(match2_auxc2)
match2_d = float(match2_auxd2)
match2_e = float(match2_auxe2)
match2_f = float(match2_auxf2)
## Busqueda de coordenadas RA/DEC del lugar del centro y 'roll'.
# Traslacion y rotacion de la transformacion.
match2_T = np.array([(match2_a), (match2_d)])
match2_R = np.array([(match2_b, match2_c), (match2_e, match2_f)])
# Coordenadas de centro de foto en pixeles.
match2_x_pix = 0
match2_y_pix = 0
match2_X_pix = np.array([(match2_x_pix), (match2_y_pix)])
match2_X_cielo = match2_T + np.dot(match2_R, match2_X_pix)
match2_RA_new = match2_X_cielo[0]
match2_DEC_new = match2_X_cielo[1]
# Calculo de angulo de 'roll'.
match2_roll_r = np.arctan2(match2_c, match2_b)
match2_roll_d = (180/np.pi)*match2_roll_r

dep2_xi = match2_RA_new/f
dep2_eta = match2_DEC_new/f
dep2_RA_r = dep1_alpha1*(np.pi/180)
dep2_DEC_r = dep1_delta1*(np.pi/180)
dep2_arg1 = np.cos(dep2_DEC_r) - dep2_eta*np.sin(dep2_DEC_r)
dep2_arg2 = np.arctan(dep2_xi/dep2_arg1)
dep2_alpha1 = dep1_alpha1 + (180/np.pi)*dep2_arg2
dep2_arg3 = np.sin(dep2_arg2)
dep2_arg4 = dep2_eta*np.cos(dep2_DEC_r) + np.sin(dep2_DEC_r)
dep2_delta1 = (180/np.pi)*np.arctan((dep2_arg3*dep2_arg4)/dep2_xi)

# Iniciamos arrays vacios.
cat_tran2 = Table([[], [], []])
conv2_largo1 = len(np_tabla1)
# Ciclo donde crea el arreglo de datos transformados.
for index in range (0, conv2_largo1):
    conv2_alpha_d = np_tabla1[index][0]
    conv2_delta_d = np_tabla1[index][1]
    conv2_mag = np_tabla1[index][2]
    # Conversion de grados a radianes.
    conv2_alpha_r = (np.pi/180)*conv2_alpha_d
    conv2_delta_r = (np.pi/180)*conv2_delta_d
    conv2_alpha_0_r = (np.pi/180)*dep2_alpha1
    conv2_delta_0_r = (np.pi/180)*dep2_delta1
    # Calculo de Xi (analogo a RA).
    conv2_xi_up = np.cos(conv2_delta_r)*np.sin(conv2_alpha_r - conv2_alpha_0_r)
    conv2_xi_down = np.sin(conv2_delta_0_r)*np.sin(conv2_delta_r) + np.cos(conv2_delta_0_r)*np.cos(conv2_delta_r)*np.cos(conv2_alpha_r - conv2_alpha_0_r)
    conv2_xi = conv2_xi_up/conv2_xi_down
    # Calculo de Eta (analogo a DEC).
    conv2_eta_up = np.cos(conv2_delta_0_r)*np.sin(conv2_delta_r) - np.sin(conv2_delta_0_r)*np.cos(conv2_delta_r)*np.cos(conv2_alpha_r - conv2_alpha_0_r)
    conv2_eta_down = conv2_xi_down
    conv2_eta = conv2_eta_up/conv2_eta_down
    # Conversion a mm.
    conv2_xi_mm = f*conv2_xi
    conv2_eta_mm = f*conv2_eta
    # Agrega el dato al arreglo.
    cat_tran2.add_row([conv2_xi_mm, conv2_eta_mm, conv2_mag])
# Guarda el nuevo catalogo.
ascii.write(cat_tran2, 'new_cat', delimiter = ' ', format = 'no_header', formats = {'col0':'% 15.5f', 'col1':'% 15.5f', 'col2':'% 15.2f'})

new_parametros2 = 'trirad=0.002 nobj=20 max_iter=3 matchrad=1 scale=1'
Match5 = 'match ' + path_stars + ' 0 1 2 ' + new_path_catalog + ' 0 1 2 ' + new_parametros2
resultado5 = subprocess.check_output(Match5, shell=True)
#Busqueda de parametros.
match3_aux1 = resultado5.find('a=')
match3_aux2 = resultado5.find('b=')
match3_aux3 = resultado5.find('c=')
match3_aux4 = resultado5.find('d=')
match3_aux5 = resultado5.find('e=')
match3_aux6 = resultado5.find('f=')
match3_aux7 = resultado5.find('sig=')
match3_aux8 = resultado5.find('Nr=')
match3_auxa1 = resultado5[match3_aux1+2:match3_aux1+25]
match3_auxb1 = resultado5[match3_aux2+2:match3_aux2+25]
match3_auxc1 = resultado5[match3_aux3+2:match3_aux3+25]
match3_auxd1 = resultado5[match3_aux4+2:match3_aux4+25]
match3_auxe1 = resultado5[match3_aux5+2:match3_aux5+25]
match3_auxf1 = resultado5[match3_aux6+2:match3_aux6+25]
match3_auxsig5 = resultado5[match3_aux7+4:match3_aux7+25]
match3_auxnr5 = resultado5[match3_aux8+3:match3_aux8+10]
match3_auxa2 = match3_auxa1.split(' ', 1)[0]
match3_auxb2 = match3_auxb1.split(' ', 1)[0]
match3_auxc2 = match3_auxc1.split(' ', 1)[0]
match3_auxd2 = match3_auxd1.split(' ', 1)[0]
match3_auxe2 = match3_auxe1.split(' ', 1)[0]
match3_auxf2 = match3_auxf1.split(' ', 1)[0]
match3_sig = match3_auxsig5.split(' ', 1)[0]
match3_nr = match3_auxnr5.split(' ', 1)[0]
match3_a = float(match3_auxa2)
match3_b = float(match3_auxb2)
match3_c = float(match3_auxc2)
match3_d = float(match3_auxd2)
match3_e = float(match3_auxe2)
match3_f = float(match3_auxf2)
## Busqueda de coordenadas RA/DEC del lugar del centro y 'roll'.
# Traslacion y rotacion de la transformacion.
match3_T = np.array([(match3_a), (match3_d)])
match3_R = np.array([(match3_b, match3_c), (match3_e, match3_f)])
# Coordenadas de centro de foto en pixeles.
match3_x_pix = 0
match3_y_pix = 0
match3_X_pix = np.array([(match3_x_pix), (match3_y_pix)])
match3_X_cielo = match3_T + np.dot(match3_R, match3_X_pix)
match3_RA_new = match3_X_cielo[0]
match3_DEC_new = match3_X_cielo[1]
# Calculo de angulo de 'roll'.
match3_roll_r = np.arctan2(match3_c, match3_b)
match3_roll_d = (180/np.pi)*match3_roll_r


dep3_xi = match3_RA_new/f
dep3_eta = match3_DEC_new/f
dep3_RA_r = dep2_alpha1*(np.pi/180)
dep3_DEC_r = dep2_delta1*(np.pi/180)
dep3_arg1 = np.cos(dep3_DEC_r) - dep3_eta*np.sin(dep3_DEC_r)
dep3_arg2 = np.arctan(dep3_xi/dep3_arg1)
dep3_alpha1 = dep2_alpha1 + (180/np.pi)*dep3_arg2
dep3_arg3 = np.sin(dep3_arg2)
dep3_arg4 = dep3_eta*np.cos(dep3_DEC_r) + np.sin(dep3_DEC_r)
dep3_delta1 = (180/np.pi)*np.arctan((dep3_arg3*dep3_arg4)/dep3_xi)


