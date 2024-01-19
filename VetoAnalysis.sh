#!/bin/bash

cd /afs/cern.ch/work/g/gpsndlhc/veto

run =  $RUNN
echo $run

python3 VetoEff.py $run