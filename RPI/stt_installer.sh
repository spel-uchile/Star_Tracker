# Install Source Extractor
printf " -----***** INSTALLING SOURCE EXTRACTOR *****----- \n"
sudo apt install sextractor

# Download Match (V0.14)
printf "\n -----***** DOWNLOADING MATCH V0.14 *****----- \n"
wget spiff.rit.edu/match/match-0.14.tar.gz
# Extract and install Match
printf "\n -----***** INSTALLING MATCH V0.14 *****----- \n"
tar -xf match-0.14.tar.gz -C .
cd match-0.14
./configure
make
make check
sudo make install
make clean
cd ..
rm -rf match-0.14.tar.gz

# Testing Source Extractor and Match
printf "\n -----***** TESTING SOURCE EXTRACTOR *****----- \n"
sextractor
printf "\n -----***** TESTING MATCH *****----- \n"
match
