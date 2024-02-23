#!/bin/bash

dir="/afs/cern.ch/work/g/gpsndlhc/veto/results"
files=()
# unfinished=0
for file in "$dir"/runs/output_*; do
    if [ -f "$file" ]; then
        size=$(stat -c %s "$file")
        if (( $size > 1000 )); then 
            files+=("$file")
        else 
            unfinished=$((unfinished+1))
        fi
    fi
done

hadd -f "$dir"/analisysResult.root ${files[@]}

# echo $unfinished
if [ "$1" = "-r" ]; then
    echo Removing condor job log files
    rm /afs/cern.ch/work/g/gpsndlhc/veto/condorJob/error/VetoAnalysis.*
    rm /afs/cern.ch/work/g/gpsndlhc/veto/condorJob/error/VetoAnalysis.*
    rm /afs/cern.ch/work/g/gpsndlhc/veto/condorJob/error/VetoAnalysis.* 
fi