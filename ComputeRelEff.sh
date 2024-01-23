#!/bin/bash
echo Add the results files 
echo " "

hadd -f ./results/output$1.root ./results/output_run100$1* 

echo " "
echo " "
echo Compute efficiency
echo " "

python3 RelativeEff.py $1
echo " "