#!/bin/bash

cd /afs/cern.ch/work/g/gpsndlhc/veto

run=$3

echo $RUNN
echo $run

python3 VetoEff.py $run
