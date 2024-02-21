#!/bin/bash

dir="/afs/cern.ch/work/g/gpsndlhc/veto/results"
files=()

for file in "$dir"/runs/output_*; do
    if [ -f "$file" ]; then
        size=$(stat -c %s "$file")
        if (( $size > 1000 )); then 
            files+=("$file")
            #hadd -f "$dir"/prova.root $file
        fi
    fi
done

hadd -f "$dir"/analisysResult.root ${files[@]}