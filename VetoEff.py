from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph, TChain, TEfficiency
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
    for row in map:
        if (row[4] == str(tofpet_channel) and row[3] == str(tofpet_id%2)):
            return int(row[0])
    return -1

def compute_time(map, board_id, tofpet_id, tofpet_channel, tfine, tac):  
    a = 0
    b = 0
    c = 0  
    for row in map:
        if (row[0] == str(board_id) and row[1] == str(tofpet_id) and row[2] == str(tofpet_channel)  and row[3] == str(tac)):
            a = float(row[4])
            b = float(row[5]) 
            c = float(row[6])
            time = (-b-(b**2-(4*a*(c-333)))**0.5)/(2*a) #https://gitlab.cern.ch/snd-scifi/software/-/wikis/Raw-data-format
            return time 
    print('oh no')
    return -1

#DS_PROPSPEED = 14.3 #cm/ns  clock cycle = 160000000 MHz -> 6,25*10^(-12) s-> 6,25*10^-3 
DS_SPEED = .2 #channels per tfine units
CLK2NS = 6.25

#prepare output file
outfile = ROOT.TFile.Open("output.root", "RECREATE")

#print(f"creating write file: {outfile}",flush=True)


mapDS = read_csv_file("./DS_SiPM_mapping.csv")
mapVeto = read_csv_file("./Veto_SiPM_mapping.csv")
calibration = read_csv_file("./qdc_cal.csv")




# read data 
data = ROOT.TChain("data")


#runList = glob("run_100*/")
runList = ['run_100793/']
for runN in runList:
    filelist = glob(f"{runN}data_*.root")
    #print(filelist)
    for file in filelist:
        #print(f"Reading {file}")
        data.Add(file)


#data.Add("run_100793/data_0000.root")
#data.Add("run_100793/data_0001.root")
#data.Add("run_100793/data_0002.root")

Nentries = data.GetEntries()

#create histos 
DSn_bins = 62
DSx_min = -.5
DSx_max = 62.5
DSVHits = ROOT.TH1D("DSVHits", "DS Vertical Hits", DSn_bins, DSx_min, DSx_max) 
DSHHits = ROOT.TH1D("DSHHits", "DS Horizontal Hits", DSn_bins, DSx_min, DSx_max)
VetoHits = ROOT.TH1D("VetoHits", "Veto Hits", DSn_bins, DSx_min, DSx_max)
TimeDiff = ROOT.TH1D("TimeDiff", "Time Difference Distribution; Ltime-Rtime; entries", 101, -100.5, 100.5)
Denominatore = ROOT.TH2D("Denominatore", "Denominatore", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)
TimeL = ROOT.TH1D("TimeL", "Time Distribution", 10000, -5000, 5000)
TimeR = ROOT.TH1D("TimeR", "Time Distribution", 10000, -5000, 5000)

Eff_Hch = ROOT.TEfficiency( "Eff_Hch", "Efficiency per DS horizontal channel", DSn_bins, DSx_min, DSx_max)
Eff_Vch = ROOT.TEfficiency( "Eff_Vch", "Efficiency per DS vertical channel", DSn_bins, DSx_min, DSx_max)
Eff_DS  = ROOT.TEfficiency( "Eff_ch", "Efficiency per DS channel", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)

Residual = ROOT.TH1D("Residual", "Position residual; x_computed - dsv bar; entries", 10001, -10000, 10000)

counter = 0
counter2 = 0
counterSameCh = 0
counterVeto = 0
relative_eff = 0

# loop on entries
for i in range(Nentries):
    if i%10000 == 0:
        print(f"Processing event {i}", end= '\r') 
    entry = data.GetEntry(i)
    
    #select ds event
    boardID = np.uint8(data.board_id)
    hitDS = (boardID == 1).sum()
    if hitDS == 3:

        counter+=1
        # DS boardID 1, V=[0,1], L=[2,3], R=[4,5]
        # Veto boardID 48 [6,7]
        tofChannel = np.uint8(data.tofpet_channel)
        tofID = np.uint8(data.tofpet_id)
        coarsetime = np.uint64(data.t_coarse)
        time = np.uint64(data.t_fine)
        qdc = np.uint64(data.v_fine)
        tac = np.uint64(data.tac)

        DStofID = tofID[ boardID==1]
        DStofCh = tofChannel[boardID==1]
        DScoarsetime = coarsetime[boardID==1]
        DStime = time[boardID == 1]
        DStac = tac[boardID == 1]

        DSRID = DStofID[DStofID>3]
        DSLID = DStofID[(DStofID>1) & (DStofID<4)]
        DSVID = DStofID[DStofID<2]

        #ask for 3 hit in totala in ds-> 1 ds R 1 ds L and 1 ds V     

        if len(DSLID) == 1 and len(DSRID) == 1 and len(DSVID) == 1:
            counter2+=1

            DSLCh = DStofCh[(DStofID>1) & (DStofID<4)]
            DSRCh = DStofCh[DStofID>3]
            DSVCh = DStofCh[DStofID<2]

            DSLtac = DStac[(DStofID>1) & (DStofID<4)]
            DSRtac = DStac[DStofID>3]
            DSVtac = DStac[DStofID<2]
            
            DSRBar = return_bar(mapDS, DSRID[0], DSRCh[0])
            DSLBar = return_bar(mapDS, DSLID[0], DSLCh[0])
            DSVBar = return_bar(mapDS, DSVID[0], DSVCh[0])
            
            if DSRBar == DSLBar: 
                DSVHits.Fill(DSVBar)
                DSHHits.Fill(DSLBar)
                Denominatore.Fill(DSVBar, DSLBar)
                vetohit = True if len( tofID[boardID == 48] ) > 0 else False
                Eff_Hch.Fill(vetohit, DSLBar)
                Eff_Vch.Fill(vetohit, DSVBar)
                Eff_DS.Fill(vetohit, DSVBar, DSLBar)

                counterSameCh+=1
                Lcoarsetime = DScoarsetime[ (DStofID > 1) & (DStofID < 4)]
                Rcoarsetime = DScoarsetime[ (DStofID > 3)]
                Ltime = DStime[ (DStofID > 1) & (DStofID < 4)]
                Rtime = DStime[ (DStofID > 3)]
                #calibratedLtime = (Lcoarsetime + compute_time(calibration, 1, DSLID[0], DSLCh[0], Ltime[0], DSLtac[0]))*CLK2NS   #in clock cycles
                #calibratedLtime = compute_time(calibration, 1, DSLID[0], DSLCh[0], Ltime[0], DSLtac[0])
                calibratedLtime = Lcoarsetime*CLK2NS
                TimeL.Fill(calibratedLtime)            

                #calibratedRtime = (Rcoarsetime + compute_time(calibration, 1, DSRID[0], DSRCh[0], Rtime[0], DSRtac[0]))*CLK2NS
                #calibratedRtime = compute_time(calibration, 1, DSRID[0], DSRCh[0], Rtime[0], DSRtac[0])
                calibratedRtime = Rcoarsetime*CLK2NS
                TimeR.Fill(calibratedRtime)

                diff = (calibratedLtime-calibratedRtime)
                TimeDiff.Fill(diff)
                xpos = 30+DS_SPEED*diff
                Residual.Fill(xpos-DSVBar)
                #print(f"ho calcolato con {Ltime} e {Rtime} la {xpos}, vedo un hit in {DSVBar}")
                vetoId = tofID[boardID == 48]
                vetoCh = tofChannel[boardID == 48]
                for i in range(len(vetoId)):                    
                    vetoBar = return_bar(mapVeto, vetoId[i], vetoCh[i])
                    VetoHits.Fill(vetoBar)

                if len(vetoId)>0: 
                    counterVeto+=1


# compute relative efficiency
first = 0
last = 0 
# compute mean over intervals of 10 channels
for i in range(10) :
    first += Eff_Vch.GetEfficiency(15+i)
    last += Eff_Vch.GetEfficiency(35+i)
first_eff = first/10
last_eff = last/10

print(f'first {first_eff}, last {last_eff}')
relative_eff = first_eff/last_eff

TimeR.Write()
TimeL.Write()
TimeDiff.Write()
DSVHits.Write() 
DSHHits.Write()
VetoHits.Write()
Denominatore.Write()
Eff_Hch.Write()
Eff_Vch.Write()
Eff_DS.Write()
Residual.Write()

outfile.Close()
Lv0Eff = counterVeto/counter2
GoodEvents = counter2/Nentries
print(f'\nRelative eff of [35,45] wrt [15,25] is {relative_eff}')
print('\nDone')
# print(f"trovo una frazione di {GoodEvents}")
# print(f"prima stima dell'efficienza di veto {Lv0Eff}")
# print(counter2)
# print(counterSameCh)

    #tofpet id per distinguere destra sinistra verticale
    #tfine per tempo entries
    #barra ds in hitplots riga 570 -> copia readcsv da task e return bar sempre in task-> prima distinguo dx/sx con tofpet poi cerco sipm per vedere stessa barra
    #copia get ds bar e faccio get veto bar 



