# 1.- Imports.
import ST_functions
import sys
import re
import commands
from astropy.table import Table
import multiprocessing
import subprocess
import numpy as np

# 2.- Define directories, names and constants values.
DIRs = ST_functions.names_and_dir()
DIR_this = DIRs[0]
DIR_img_fits = DIRs[1]
DIR_stars = DIRs[2]
DIR_first_match = DIRs[3]
DIR_sext = DIRs[4]
DIR_proj_cat1 = DIRs[5]
DIR_proj_cat2 = DIRs[6]
DIR_normal_cat = DIRs[7]
fits_name = DIRs[8]
const = ST_functions.st_constants()
x_pix = const[0]
y_pix = const[1]
cmos2pix = const[2]

# 3.- Receives and reviews the initial data.
st_args = sys.argv
len_arg = len(st_args)
pic_name, cat_division = ST_functions.rev_initial_data(st_args, len_arg)

# - First review.
print '-.'*30
print 'REVIEW - 1:'
print 'Initial arguments:', st_args
print 'Image name:', pic_name
print 'DIR_this: ', DIR_this
print '-.'*30

# 4.- Generate FITS image and execute SExtractor.
ST_functions.generate_fits(pic_name, fits_name)
ST_functions.apply_sext(DIR_sext, DIR_img_fits, fits_name, x_pix, y_pix, cmos2pix)

# 5.- Apply first 'Match' routine.
if cat_division == 10:
    ra_dec_list = ST_functions.ra_dec_10()
else:
    ra_dec_list = ST_functions.ra_dec_5()
pool = multiprocessing.Pool(multiprocessing.cpu_count())
first_match_results = pool.map(ST_functions.call_match, ra_dec_list)
match1_tabla1 = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))
for i, (status1, resultado1) in enumerate(first_match_results):
    RA1, DEC1 = ra_dec_list[i]
    if status1 == 0:
        match1_aux1 = resultado1.find('sig=')
        match1_aux2 = resultado1.find('Nr=')
        match1_auxsig1 = resultado1[match1_aux1+4:match1_aux1+25]
        match1_auxnr1 = resultado1[match1_aux2+3:match1_aux2+10]
        match1_sig1 = match1_auxsig1.split(' ', 1)[0]
        match1_nr1 = match1_auxnr1.split(' ', 1)[0]
        match1_tabla1.add_row([str(RA1), str(DEC1), match1_sig1, match1_nr1])

if len(match1_tabla1) == 0:
    print 'There is no match!'
else:
    # Reordena la tabla por menor 'Nr'.
    match1_tabla1.sort('Nr')
    match1_tabla1.reverse()
    print match1_tabla1

print ' --- END --- '


## 6.- Match: First iteration.
print multiprocessing.cpu_count() # Count cores names.
# Define regular expresion for Match.
match_reg = re.compile(r"a=(-*\d\.\d+e...) b=(-*\d\.\d+e...) c=(-*\d\.\d+e...) d=(-*\d\.\d+e...) e=(-*\d\.\d+e...)"
                       r" f=(-*\d\.\d+e...) sig=(-*\d\.\d+e...) Nr=(-*\d+) Nm=(-*\d+)"
                       r" sx=(-*\d\.\d+e...) sy=(-*\d\.\d+e...) ")
# Definimos el path para el catalogo.
path_catalog1 = DIR_proj_cat1 + 'cat_RA_'
# Definimos parametros de 'match'.
param1 = 'trirad=0.002 nobj=15 max_iter=1 matchrad=1 scale=1'
# Inicializamos una tabla.
match1_tabla1 = Table(names=('RA_center', 'DEC_center', 'sig', 'Nr'))

# def call_match(ra_dec):
#     RA1, DEC1 = ra_dec
#     # Transform RA and DEC in string and make the path for catalog.
#     path_catalog2 = str(RA1) + '_DEC_' + str(DEC1)
#     path_catalog3 = path_catalog1 + path_catalog2
#     # Do Match.
#     Match1 = 'match ' + DIR_stars + ' 0 1 2 ' + path_catalog3 + ' 0 1 2 ' + parametros1
#     status1, resultado1 = commands.getstatusoutput(Match1)
#     return status1, resultado1

# Create the list of parameters.
ra_dec = [(ra, dec) for ra in range(0, 360, 10) for dec in range(-80, 90, 10)]
pool = multiprocessing.Pool(multiprocessing.cpu_count())
results = map(ST_functions.call_match, ra_dec, DIR_stars, DIR_proj_cat2, param1)

print ' --- RESULTS --- '
print results

for i, (status1, resultado1) in enumerate(results):
    RA1, DEC1 = ra_dec[i]
    if status1 == 0:
        print ' --- '
        print ra_dec[i]
        print ' --- '
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
    Match2 = 'match ' + DIR_stars + ' 0 1 2 ' + path_catalog5 + ' 0 1 2 ' + parametros1
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
    print match1_tabla1
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
    Match3 = 'match ' + DIR_stars + ' 0 1 2 ' + path_catalog7 + ' 0 1 2 ' + parametros1
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
    # Prints.
    print '--/'*20
    print 'Los resultados son:'
    print 'RA_center =', match1_RA_new
    print 'DEC_center =', match1_DEC_new
    print 'Roll =', match1_roll_d
    print 'sig =', match1_sig3
    print 'Nr =', match1_nr3
    print 'Nm =', match1_nm3
    print 'Catalogo => ', 'RA =', match1_RA, '/', 'DEC =', match1_DEC
    print '--/'*20