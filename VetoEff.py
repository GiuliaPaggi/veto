from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph, TChain
import numpy as np
import argparse
import ROOT
import os
import time as t
from glob import glob
import csv

def read_csv_file(file_path):
    """Read the contents of a CSV file and return the data as a list of lists."""
    with open(file_path, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        map = [row for row in csvreader]
    return map


def return_bar(map, tofpet_id, tofpet_channel):    
    #print(f" in funzione leggo {tofpet_id} e {tofpet_channel}")
    for row in map:
        if (row[4] == str(tofpet_channel) and row[3] == str(tofpet_id%2)):
            return int(row[0])
    return -1

#prepare output file
outfile = ROOT.TFile.Open("output.root", "RECREATE")
#print(f"creating write file: {outfile}",flush=True)
outfile.Close()

mapDS = read_csv_file("./DS_SiPM_mapping.csv")
mapVeto = read_csv_file("./Veto_SiPM_mapping.csv")


# read data 
data = ROOT.TChain("data")

"""
runList = glob("run_100*/")
for runN in runList:
    filelist = glob(f"{runN}data_*.root")
    #print(filelist)
    for file in filelist:
        #print(f"Reading {file}")
        data.Add(file)
"""
data.Add("run_100793/data_0000.root")
Nentries = data.GetEntries()
counter = 0
counter2 = 0
countTof4 = 0
counterSameCh = 0
for i in range(Nentries):
    if i%10000 == 0:
        print(i, end= '\r') 
    entry = data.GetEntry(i)
    #select ds event

    boardID = np.uint8(data.board_id)
    hitDS = (boardID == 1).sum()
    if hitDS == 3:
        counter+=1
        # DS boardID 1, vertical = [0,1], L=[2,3], R=[4,5]
        tofChannel = np.uint8(data.tofpet_channel)
        tofID = np.uint8(data.tofpet_id)
        time = np.uint64(data.t_fine)

        DStofID = tofID[ boardID==1]
        DStofCh = tofChannel[boardID==1]
        DStime = time[boardID == 1]
        if (DStofID == 4).sum():
            countTof4+=1
        DSRID = DStofID[DStofID>3]
        DSLID = DStofID[(DStofID>1) & (DStofID<4)]
        DSVIS = DStofID[DStofID<2]
        if len(DSLID) == 1 & len(DSRID) == 1 & len(DSLID) == 1:
            counter2+=1
            DSLCh = DStofCh[(DStofID>1) & (DStofID<4)]
            DSRCh = DStofCh[DStofID>3]
            #print("###################################################")
            DSRBar = return_bar(mapDS, DSRID[0], DSRCh[0])
            DSLBar = return_bar(mapDS, DSLID[0], DSLCh[0])
            #print(f"cerco L id {DSLID[0]} e {DSLCh[0]} trovo {DSLBar}, R {DSRID[0]} e {DSRCh[0]} e trovo {DSRBar}")
            if DSRBar == DSLBar: 
                counterSameCh+=1
                Ltime = DStime[ (DStofID > 1) & (DStofID < 4)]
                Rtime = DStime[ (DStofID > 3)]
                print(f"i tempi sono {Rtime} e {Ltime}")



print('\n',counter)
print(counter2)
print(countTof4)
print(counterSameCh)

    #tofpet id per distinguere destra sinistra verticale
    #tfine per tempo entries
    #barra ds in hitplots riga 570 -> copia readcsv da task e return bar sempre in task-> prima distinguo dx/sx con tofpet poi cerco sipm per vedere stessa barra
    #copia get ds bar e faccio get veto bar 



