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
cd ../RPi

# Testing Source Extractor and Match
printf "\n -----***** TESTING SOURCE EXTRACTOR *****----- \n"
cmd_sex="source-extractor"
sex_status=$?
[ $sex_status -eq 0 ] && echo "$cmd_sex was successfully executed!"
printf "\n -----***** TESTING MATCH *****----- \n"
cmd_match="match"
match_status=$?
[ $match_status -eq 0 ] && echo "$cmd_match was successfully executed!"
