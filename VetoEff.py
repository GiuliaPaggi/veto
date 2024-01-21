from ROOT import TH1, TH1D, TH1F, TCanvas,TFile, gROOT, gDirectory, gSystem, TGraph, TChain, TEfficiency
import numpy as np
import ROOT
import os, sys
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

#############
# read data #
#############

runN = sys.argv[1]
runDirectory = f"/eos/experiment/sndlhc/raw_data/commissioning/veto/run_{runN}/"


data = ROOT.TChain("data")

filelist = glob(f"{runDirectory}data_all*.root")

for file in filelist:
    data.Add(file)

# read mapping cvs
mapDS = read_csv_file("./SiPMmaps/DS_SiPM_mapping.csv")
mapVeto = read_csv_file("./SiPMmaps/Veto_SiPM_mapping.csv")
calibration = read_csv_file(f"{runDirectory}qdc_cal.csv")

#prepare output file
filename = f"./results/output_run{runN}.root"
outfile = ROOT.TFile.Open(filename, "RECREATE")

#################
# Define histos #
#################

DSn_bins = 63
DSx_min = -.5
DSx_max = 62.5

# Hits info 
DSVHits = ROOT.TH1D("DSVHits", "DS Vertical Hits; # ds v channel; entries", DSn_bins, DSx_min, DSx_max) 
DSHHits = ROOT.TH1D("DSHHits", "DS Horizontal Hits; # ds h channel; entries", DSn_bins, DSx_min, DSx_max)
VetoHits = ROOT.TH1D("VetoHits", "Veto Hits; # veto channel; entries", DSn_bins, DSx_min, DSx_max)
VetoHitMultiplicity = ROOT.TH1D("VetoHitMultiplicity", "Veto Hit Multiplicity; # hits per event; entries", 20, -.5, 19.5)
Cosmic_VetoHits = ROOT.TH1D("Cosmic_VetoHits", "Veto Hits in cosmics events; # veto channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitMultiplicity = ROOT.TH1D("Cosmic_VetoHitMultiplicity", "Veto Hit Multiplicity in cosmic ray events; # hits per event; entries", 20, -.5, 19.5)
Bkg_VetoHits = ROOT.TH1D("Bkg_VetoHits", "Veto Hits in not cosmics events; # veto channel; entries", DSn_bins, DSx_min, DSx_max)
Bkg_VetoMultiplicity = ROOT.TH1D("Bkg_VetoMultiplicity", "Veto Hit Multiplicity in not cosmics; # hits per event; entries", 20, -.5, 19.5)
Noise_VetoHits = ROOT.TH1D("Noise_VetoHits", "Veto Hits w/o ds hits; # veto channel; entries", DSn_bins, DSx_min, DSx_max)
Noise_VetoMultiplicity = ROOT.TH1D("Noise_VetoMultiplicity", "Veto Hit Multiplicity w/o ds hits; # hits per event; entries", 20, -.5, 19.5)


# qdc
DSLQdc = ROOT.TH1D("DSLQdc", "DSLQdc; qdc; entries", DSn_bins, DSx_min, DSx_max)
DSRQdc = ROOT.TH1D("DSRQdc", "DSRQdc; qdc; entries", DSn_bins, DSx_min, DSx_max)
DSVQdc = ROOT.TH1D("DSVQdc", "DSVQdc; qdc; entries", DSn_bins, DSx_min, 150)
VetoQdc = ROOT.TH1D("VetoQdc", "VetoQdc; qdc; entries", 68, -5.5, DSx_max)
VetoQDCPerChannel = ROOT.TH2D("VetoQDCPerChannel", "VetoQDCPerChannel; veto channel; qdc ", DSn_bins, DSx_min, DSx_max, 68, -5.5, DSx_max)
Cosmic_VetoQdc = ROOT.TH1D("Cosmic_VetoQdc", "Cosmic_VetoQdc; veto channel; qdc ", 68, -5.5, DSx_max)
Cosmic_VetoQDCPerChannel = ROOT.TH2D("Cosmic_VetoQDCPerChannel", "Cosmic_VetoQDCPerChannel; veto channel; qdc ", DSn_bins, DSx_min, DSx_max, 68, -5.5, DSx_max)
Bkg_VetoQdc = ROOT.TH1D("Bkg_VetoQdc", "Bkg_VetoQdc; veto channel; qdc ", 68, -5.5, DSx_max)
Noise_VetoQdc = ROOT.TH1D("Noise_VetoQdc", "Noise_VetoQdc; veto channel; qdc ", 68, -5.5, DSx_max)

# Efficiency
Denominatore = ROOT.TH2D("Denominatore", "Denominatore", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)

Eff_Hch = ROOT.TEfficiency( "Eff_Hch", "Efficiency per DS horizontal channel; ds h channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
Eff_Vch = ROOT.TEfficiency( "Eff_Vch", "Efficiency per DS vertical channel; ds v channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
Eff_DS  = ROOT.TEfficiency( "Eff_ch", "Efficiency per DS channel; ds v channel number; ds h channel number", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)


relative_eff = 0

###################
# loop on entries #
###################

Nentries = data.GetEntries()
for i in range(Nentries):
    entry = data.GetEntry(i)
    
    boardID = np.uint8(data.board_id)
    tofChannel = np.uint8(data.tofpet_channel)
    tofID = np.uint8(data.tofpet_id)
    qdc = np.asarray(data.value, float)
    
    # veto info
    vetoId = tofID[boardID == 48]
    vetoCh = tofChannel[boardID == 48]
    vetoQdc = qdc[boardID == 48]

    vetoMultiplicity = len(vetoId)
    VetoHitMultiplicity.Fill(vetoMultiplicity)

    if vetoMultiplicity > 0:        
        vetoBars = [return_bar(mapVeto, vetoId[i], vetoCh[i]) for i in range(vetoMultiplicity)]
        
        for i in range(vetoMultiplicity):
            if (vetoId[i]%2 == 1) and (vetoCh[i] == 53): print(f'Sto cercando 19 e trovo {vetoBars[i]}')
            if (vetoId[i]%2 == 1) and (vetoCh[i] == 37): print(f'Sto cercando 23 e trovo {vetoBars[i]}')
            
            VetoHits.Fill(vetoBars[i])
            VetoQdc.Fill(vetoQdc[i])
            VetoQDCPerChannel.Fill(vetoBars[i], vetoQdc[i])


    
    # DS info
    DStofID = tofID[boardID == 1]
    DsMultiplicity = len(DStofID)

    DStofCh = tofChannel[boardID == 1]
    DSQdc = qdc[boardID == 1]

    #############################
    # select cosmic rays events #
    #############################

    if DsMultiplicity == 3:

        # DS boardID 1, V=[0,1], L=[2,3], R=[4,5]
        # Veto boardID 48 [6,7]
        DSRID = DStofID[DStofID>3]
        DSLID = DStofID[(DStofID>1) & (DStofID<4)]
        DSVID = DStofID[DStofID<2]

        #########################
        # select cosmics events #
        #########################

        #ask for 3 hit in total in ds-> 1 ds R 1 ds L and 1 ds V     

        if len(DSLID) == 1 and len(DSRID) == 1 and len(DSVID) == 1:

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
            
            # cut on qdc to ensure is a MIP signal 

            if (20 < LQdc[0] < 30) and (18 < RQdc[0] < 28) and (45 < VQdc[0] < 65) and DSRBar == DSLBar: 
                DSVHits.Fill(DSVBar)
                DSHHits.Fill(DSLBar)
                Denominatore.Fill(DSVBar, DSLBar)
                vetohit = True if vetoMultiplicity > 0 else False
                Eff_Hch.Fill(vetohit, DSLBar)
                Eff_Vch.Fill(vetohit, DSVBar)
                Eff_DS.Fill(vetohit, DSVBar, DSLBar)
                
                if vetoMultiplicity > 0: 

                    Cosmic_VetoHitMultiplicity.Fill(vetoMultiplicity)

                    for i in range (vetoMultiplicity) :
                        Cosmic_VetoHits.Fill(vetoBars[i])
                        Cosmic_VetoQdc.Fill(vetoQdc[i])
                        Cosmic_VetoQDCPerChannel.Fill(vetoBars[i], vetoQdc[i])

                    
            else:
                
                Bkg_VetoMultiplicity.Fill(vetoMultiplicity)

                if vetoMultiplicity > 0:
                    for i in vetoBars : Bkg_VetoHits.Fill(i)
                    
                    for i in vetoQdc : Bkg_VetoQdc.Fill(i)

    ####################
    # study veto noise #
    ####################

    elif DsMultiplicity == 0 and vetoMultiplicity > 0:
        
        Noise_VetoMultiplicity.Fill(vetoMultiplicity)
        for i in range(vetoMultiplicity):
            Noise_VetoHits.Fill(vetoBars[i])
            Noise_VetoQdc.Fill(vetoQdc[i])

############################
# write histo to root file #
############################

#hits information
DSVHits.Write() 
DSHHits.Write()
VetoHits.Write()
VetoHitMultiplicity.Write()
Cosmic_VetoHits.Write()
Cosmic_VetoHitMultiplicity.Write()
Bkg_VetoHits.Write()
Bkg_VetoMultiplicity.Write()
Noise_VetoHits.Write()
Noise_VetoMultiplicity.Write()

#efficiencies histo
Denominatore.Write()
Eff_Hch.Write()
Eff_Vch.Write()
Eff_DS.Write()

#ds qdc distribution
DSLQdc.Write()
DSRQdc.Write()
DSVQdc.Write()

#veto qdc distribution
VetoQDCPerChannel.Write()
VetoQdc.Write()
Cosmic_VetoQdc.Write()
Bkg_VetoQdc.Write()
Noise_VetoQdc.Write()

outfile.Close()

print('Done')
