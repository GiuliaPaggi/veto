from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph, TChain, TEfficiency
import numpy as np
import ROOT
import os, sys
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

print(str(sys.argv[1]))

runN = sys.argv[1]
runDirectory = f"/eos/experiment/sndlhc/raw_data/commissioning/veto/run_{runN}/"



mapDS = read_csv_file("./SiPMmaps/DS_SiPM_mapping.csv")
mapVeto = read_csv_file("./SiPMmaps/Veto_SiPM_mapping.csv")
calibration = read_csv_file(f"{runDirectory}qdc_cal.csv")




# read data 
data = ROOT.TChain("data")



#prepare output file
outfile = ROOT.TFile.Open(f"output_run{runN}.root", "RECREATE")

filelist = glob(f"{runDirectory}data_all*.root")

for file in filelist:
    data.Add(file)


Nentries = data.GetEntries()

#create histos 
DSn_bins = 63
DSx_min = -.5
DSx_max = 62.5
DSVHits = ROOT.TH1D("DSVHits", "DS Vertical Hits", DSn_bins, DSx_min, DSx_max) 
DSHHits = ROOT.TH1D("DSHHits", "DS Horizontal Hits", DSn_bins, DSx_min, DSx_max)
VetoHits = ROOT.TH1D("VetoHits", "Veto Hits", DSn_bins, DSx_min, DSx_max)
All_VetoHitMultiplcity = ROOT.TH1D("All_VetoHitMultiplcity", "Veto Hit Multiplcity in all events", 20, -.5, 19.5)
Cosmic_VetoHitMultiplcity = ROOT.TH1D("Cosmic_VetoHitMultiplcity", "Veto Hit Multiplcity in cosmic ray events", 20, -.5, 19.5)

DSLQdc = ROOT.TH1D("DSLQdc", "DSLQdc", DSn_bins, DSx_min, DSx_max)
DSRQdc = ROOT.TH1D("DSRQdc", "DSRQdc", DSn_bins, DSx_min, DSx_max)
DSVQdc = ROOT.TH1D("DSVQdc", "DSVQdc", DSn_bins, DSx_min, 150)
VetoQdc = ROOT.TH1D("VetoQdc", "VetoQdc", 83, -20.5, DSx_max)
VetoQdcPerBar = ROOT.TH2D("VetoQdcPerBar", "VetoQdcPerBar", 83, -20.5, DSx_max, 83, -20.5, DSx_max) 
VetoQDCPerChannel = ROOT.TH2D("VetoQDCPerChannel", "VetoQDCPerChannel; veto channel; qdc ", 83, -20.5, DSx_max, 83, -20.5, DSx_max)

TimeDiff = ROOT.TH1D("TimeDiff", "Time Difference Distribution; Ltime-Rtime; entries",  41, -20.5, 20.5)
Denominatore = ROOT.TH2D("Denominatore", "Denominatore", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)
TimeL = ROOT.TH1D("TimeL", "Time Distribution", 41, -20.5, 20.5)
TimeR = ROOT.TH1D("TimeR", "Time Distribution", 41, -20.5, 20.5)

Eff_Hch = ROOT.TEfficiency( "Eff_Hch", "Efficiency per DS horizontal channel; ds h channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
Eff_Vch = ROOT.TEfficiency( "Eff_Vch", "Efficiency per DS vertical channel; ds v channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
Eff_DS  = ROOT.TEfficiency( "Eff_ch", "Efficiency per DS channel; ds v channel number; ds h channel number", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)

Residual = ROOT.TH1D("Residual", "Position residual; x_computed - dsv bar; entries", 201, -200.5, 200.5)

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
        time = np.asarray(data.timestamp, float)
        qdc = np.asarray(data.value, float)

        # veto info
        vetoId = tofID[boardID == 48]
        vetoMultiplicity = len(vetoId)
        All_VetoHitMultiplcity.Fill(vetoMultiplicity)

        vetoCh = tofChannel[boardID == 48]
        vetoQdc = qdc[boardID == 48]

        if vetoMultiplicity > 0:        
            vetoBars = [return_bar(mapVeto, vetoId[i], vetoCh[i]) for i in range(vetoMultiplicity)]
            

            for i in range(vetoMultiplicity):
                if (vetoId[i]%2 == 1) and (vetoCh[i] == 53): print(f'Sto cercando 19 e trovo {vetoBars[i]}')
                if (vetoId[i]%2 == 1) and (vetoCh[i] == 37): print(f'Sto cercando 23 e trovo {vetoBars[i]}')
                
                VetoQdc.Fill(vetoQdc[i])
                VetoQDCPerChannel.Fill(vetoBars[i], vetoQdc[i])

        # DS info
        DStofID = tofID[ boardID==1]
        DStofCh = tofChannel[boardID==1]
        DStime = time[boardID == 1]
        DSQdc = qdc[boardID == 1]

        DSRID = DStofID[DStofID>3]
        DSLID = DStofID[(DStofID>1) & (DStofID<4)]
        DSVID = DStofID[DStofID<2]


        #ask for 3 hit in total in ds-> 1 ds R 1 ds L and 1 ds V     

        if len(DSLID) == 1 and len(DSRID) == 1 and len(DSVID) == 1:
            counter2+=1

            DSLCh = DStofCh[(DStofID>1) & (DStofID<4)]
            DSRCh = DStofCh[DStofID>3]
            DSVCh = DStofCh[DStofID<2]
           
            DSRBar = return_bar(mapDS, DSRID[0], DSRCh[0])
            DSLBar = return_bar(mapDS, DSLID[0], DSLCh[0])
            DSVBar = return_bar(mapDS, DSVID[0], DSVCh[0])
            if (DSVID[0]%2 == 0) and (DSVCh[0] == 54) : print(f'Sto cercando 11 ma trovo {DSVBar}')

            
            LQdc = DSQdc[(DStofID>1) & (DStofID<4)]
            RQdc = DSQdc[DStofID>3]
            VQdc = DSQdc[DStofID<2]

            DSLQdc.Fill(LQdc)
            DSRQdc.Fill(RQdc)
            DSVQdc.Fill(VQdc)
            
            if (20 < LQdc[0] < 30) and (18 < RQdc[0] < 28) and (45 < VQdc[0] < 65) and DSRBar == DSLBar: 
                DSVHits.Fill(DSVBar)
                DSHHits.Fill(DSLBar)
                Denominatore.Fill(DSVBar, DSLBar)
                vetohit = True if len( tofID[boardID == 48] ) > 0 else False
                Eff_Hch.Fill(vetohit, DSLBar)
                Eff_Vch.Fill(vetohit, DSVBar)
                Eff_DS.Fill(vetohit, DSVBar, DSLBar)
                

                Cosmic_VetoHitMultiplcity.Fill(len(vetoId))

                for i in vetoBars :
                    VetoHits.Fill(i)


                if len(vetoId)>0: 
                    counterVeto+=1


# compute relative efficiency
first = 0
centre = 0
last = 0 
# compute mean over intervals of 10 channels
for i in range(10) :
    first += Eff_Vch.GetEfficiency(15+i)
    centre += Eff_Vch.GetEfficiency(25+i)
    last += Eff_Vch.GetEfficiency(35+i)
first_eff = first/10
centre_eff = centre/10
last_eff = last/10

DSVHits.Write() 
DSHHits.Write()
VetoHits.Write()

Denominatore.Write()
Eff_Hch.Write()
Eff_Vch.Write()
Eff_DS.Write()

DSLQdc.Write()
DSRQdc.Write()
DSVQdc.Write()
VetoQdcPerBar.Write()
VetoQDCPerChannel.Write()
VetoQdc.Write()

All_VetoHitMultiplcity.Write()
Cosmic_VetoHitMultiplcity.Write()

outfile.Close()

with open('textfile_run{runN}.txt', 'w') as f:
     f.write('Mean efficiency in first region '+str(first_eff)+' in the central region '+str(centre_eff)+ ' and in the last region '+str(last_eff)+
             '\nThe relative efficiency first/last is '+ str(first_eff/last_eff)+', the central/last is '+str(centre_eff/last_eff))

print('Done')