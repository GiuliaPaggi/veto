#!/bin/bash

cd /afs/cern.ch/work/g/gpsndlhc/veto

run=$3

python3 VetoEff.py $run
