printf "\n -----***** EXCTRACTING NORMAL CATALOG *****----- \n"
cd ..
tar -xf Normal.tar.gz -C "$PWD/RPi/Catalog/RPi/"
printf "\n -----***** EXCTRACTING PROJECTED CATALOG *****----- \n"
tar -xf Projected.tar.gz -C "$PWD/RPi/Catalog/RPi"

