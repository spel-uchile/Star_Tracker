# Install Source Extractor
printf " -----***** INSTALLING SOURCE EXTRACTOR *****----- \n"
sudo apt install sextractor

# Extract and install Match V0.14
printf "\n -----***** INSTALLING MATCH V0.14 *****----- \n"
cd ..
tar -xf match-0.14.tar.gz -C .
cd match-0.14
./configure
make
make check
sudo make install
make clean
cd ../RPI

# Testing Source Extractor and Match
printf "\n -----***** TESTING SOURCE EXTRACTOR *****----- \n"
source-extractor
printf "\n -----***** TESTING MATCH *****----- \n"
match
