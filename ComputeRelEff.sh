#!/bin/bash
echo Add the results files 
echo " "

hadd -f ./results/output.root ./results/output_run* 

echo " "
echo " "
echo Compute efficiency
echo " "

python3 RelativeEff.py
echo " "