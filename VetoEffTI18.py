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


def return_ch(map, tofpet_id, tofpet_channel):    
    for row in map:
        if (row[4] == str(tofpet_channel) and row[3] == str(tofpet_id%2)):
            #print(f'pin {row[4]} tof id {row[3]} returnano {row[0]} ')
            return int(row[0])
    return -1

def return_bar(map, tofpet_id, tofpet_channel):    
    for row in map:
        if (row[4] == str(tofpet_channel) and row[3] == str(tofpet_id%2)):
            return int(np.floor((int(row[0])-1)/8))
    return -1

def is_single_bar(list):
    if all(i == list[0] for i in list) :
        return int(list[0])+1
    else : 
        return 0

# scifi 1x [11,17,28] 1y [29,3,30]

#############
# read data #
#############

runN = sys.argv[1]
#runDirectory = f"/eos/experiment/sndlhc/raw_data/commissioning/veto/run_{runN}/"
runDirectory = f"/eos/experiment/sndlhc/raw_data/commissioning/2024/run_00{runN}/"


data = ROOT.TChain("data")

filelist = glob(f"{runDirectory}data_*.root")

for file in filelist:
    data.Add(file)

# read mapping cvs
mapVeto = read_csv_file("./SiPMmaps/Veto_SiPM_mapping.csv")

#prepare output file
filename = f"./results/output_run{runN}.root"
outfile = ROOT.TFile.Open(filename, "RECREATE")

#################
# Define histos #
#################

DSn_bins = 58
DSx_min = -.5
DSx_max = 57.5

# Hits info 
V1LHits = ROOT.TH1D("V1LHits", "V1 L Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
V1LHitsperBar = ROOT.TH1D("V1LHitsperBar", "V1 L Hits per Bar; veto bar; entries", 7, 0, 7)
V1RHits = ROOT.TH1D("V1RHits", "V1 R Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
V1RHitsperBar = ROOT.TH1D("V1RHitsperBar", "V1 R Hits per Bar; veto bar; entries", 7, 0, 7)

V2LHits = ROOT.TH1D("V2LHits", "V2 L Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
V2LHitsperBar = ROOT.TH1D("V2LHitsperBar", "V2 L Hits per Bar; veto bar; entries", 7, 0, 7)
V2RHits = ROOT.TH1D("V2RHits", "V2 R Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
V2RHitsperBar = ROOT.TH1D("V2RHitsperBar", "V2 R Hits per Bar; veto bar; entries", 7, 0, 7)

VetoHits = ROOT.TH1D("VetoHits", "Veto Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
VetoHitsperBar = ROOT.TH1D("VetoHitsperBar", "Veto Hits per Bar; veto bar; entries", 7, 0, 7)
VetoHitMultiplicity = ROOT.TH1D("VetoHitMultiplicity", "Veto Hit Multiplicity;  Hits per event; entries", 20, -.5, 19.5)
Cosmic_V1Hits = ROOT.TH1D("Cosmic_V1Hits", "Cosmic Veto 1 Hits;  channel; entries", DSn_bins, DSx_min, DSx_max) 
Cosmic_V2Hits = ROOT.TH1D("Cosmic_V2Hits", "Cosmic Veto 2 Hits; channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_V1HitsperBar = ROOT.TH1D("Cosmic_V1HitsperBar", "Cosmic Veto 1 Hits perBar;  bar; entries", 7, 0, 7) 
Cosmic_V2HitsperBar = ROOT.TH1D("Cosmic_V2HitsperBar", "Cosmic Veto 2 Hits perBar; bar; entries", 7, 0, 7)
Cosmic_VetoHits = ROOT.TH1D("Cosmic_VetoHits", "Veto Hits in cosmics events;  veto channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitsperBar = ROOT.TH1D("Cosmic_VetoHitsperBar", "Cosmic_Veto Hits per Bar; veto channel; entries", 7, 0, 7)
Cosmic_VetoHitsperPosition = ROOT.TH1D("Cosmic_VetoHitsperPosition", "Cosmic_VetoHitsperPosition; ds V channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitMultiplicity = ROOT.TH1D("Cosmic_VetoHitMultiplicity", "Veto Hit Multiplicity in cosmic ray events;  Hits per event; entries", 20, -.5, 19.5)
Bkg_VetoHits = ROOT.TH1D("Bkg_VetoHits", "Veto Hits in not cosmics events; veto channel; entries", DSn_bins, DSx_min, DSx_max)
Bkg_VetoMultiplicity = ROOT.TH1D("Bkg_VetoMultiplicity", "Veto Hit Multiplicity in not cosmics; Hits per event; entries", 20, -.5, 19.5)
Noise_VetoHits = ROOT.TH1D("Noise_VetoHits", "Veto Hits w/o ds Hits;  veto channel; entries", DSn_bins, DSx_min, DSx_max)
Noise_VetoMultiplicity = ROOT.TH1D("Noise_VetoMultiplicity", "Veto Hit Multiplicity w/o ds Hits;  Hits per event; entries", 20, -.5, 19.5)
Simp_perBar = ROOT.TH2D("Simp_perBar", "Simp_perBar", 7, 0, 7, 9, 0, 9)
 
# qdc
qdcbin = 220
qdc_min = -20
qdc_max = 200

Scifi1xQdc = ROOT.TH1D("Scifi1xQdc", "Scifi1xQdc; qdc; entries", 100, -24.5, 25.5)
Scifi1yQdc = ROOT.TH1D("Scifi1yQdc", "Scifi1yQdc; qdc; entries", 100, -24.5, 25.5)

V1LQdc = ROOT.TH1D("V1LQdc", "V1LQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V1RQdc = ROOT.TH1D("V1RQdc", "V1RQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V1Qdc_RvsL = ROOT.TH2D("V1Qdc_RvsL", "V1Qdc_RvsL; V1 R channel; V1 L channel", qdcbin, qdc_min, qdc_max, qdcbin, qdc_min, qdc_max)
V1QdcDiff = ROOT.TH1D("V1QdcDiff", "V1Qdc Difference; R-L QDC; Entries", 200, -100, 100)

V2LQdc = ROOT.TH1D("V2LQdc", "V2LQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQdc = ROOT.TH1D("V2RQdc", "V2RQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V2Qdc_RvsL = ROOT.TH2D("V2Qdc_RvsL", "V2Qdc_RvsL; V2 R channel; V2 L channel", qdcbin, qdc_min, qdc_max, qdcbin, qdc_min, qdc_max)
V2QdcDiff = ROOT.TH1D("V2QdcDiff", "V2Qdc Difference; R-L QDC; Entries", 200, -100, 100)


V1RQdc_max = ROOT.TH1D("V1RQdc_max", "V1RQdc_max; v1r qdc; entries", qdcbin, qdc_min, qdc_max)
V1RQdc_others = ROOT.TH1D("V1RQdc_others", "V1RQdc_others; v1r qdc; entries", qdcbin, qdc_min, qdc_max)
V1RQdc_single = ROOT.TH1D("V1RQdc_single", "V1RQdc_single; v1r qdc; entries", qdcbin, qdc_min, qdc_max)
V1RQdc_residual = ROOT.TH1D("V1RQdc_residual", "V1RQdc_residual; v1R qdc max - others; entries", 400, -200, 200)

V1LQdc_max = ROOT.TH1D("V1LQdc_max", "V1LQdc_max; v1l qdc; entries", qdcbin, qdc_min, qdc_max)
V1LQdc_others = ROOT.TH1D("V1LQdc_others", "V1LQdc_others; v1l qdc; entries", qdcbin, qdc_min, qdc_max)
V1LQdc_single = ROOT.TH1D("V1LQdc_single", "V1LQdc_single; v1l qdc; entries", qdcbin, qdc_min, qdc_max)
V1LQdc_residual = ROOT.TH1D("V1LQdc_residual", "V1LQdc_residual; v1L qdc max - others; entries", 400, -200, 200)

V2RQdc_max = ROOT.TH1D("V2RQdc_max", "V2RQdc_max; v2r qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQdc_others = ROOT.TH1D("V2RQdc_others", "V2RQdc_others; v2r qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQdc_single = ROOT.TH1D("V2RQdc_single", "V2RQdc_single; v2r qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQdc_residual = ROOT.TH1D("V2RQdc_residual", "V2RQdc_residual; v2R qdc max - others; entries", 400, -200, 200)

V2LQdc_max = ROOT.TH1D("V2LQdc_max", "V2LQdc_max; v2L qdc; entries", qdcbin, qdc_min, qdc_max)
V2LQdc_others = ROOT.TH1D("V2LQdc_others", "V2LQdc_others; v2L qdc; entries", qdcbin, qdc_min, qdc_max)
V2LQdc_single = ROOT.TH1D("V2LQdc_single", "V2LQdc_single; v2L qdc; entries", qdcbin, qdc_min, qdc_max)
V2LQdc_residual = ROOT.TH1D("V2LQdc_residual", "V2LQdc_residual; v2L qdc max - others; entries", 400, -200, 200)

VetoQdc = ROOT.TH1D("VetoQdc", "VetoQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
VetoQDCPerChannel = ROOT.TH2D("VetoQDCPerChannel", "VetoQDCPerChannel; veto channel; qdc ", DSn_bins, DSx_min, DSx_max, qdcbin, qdc_min, qdc_max)
VetoQDCPerPosition = ROOT.TH2D("VetoQDCPerPosition", "VetoQDCPerPosition; dsV channel; qdc ", DSn_bins, DSx_min, DSx_max, qdcbin, qdc_min, qdc_max)
VetoQDCPerBar = ROOT.TH2D("VetoQDCPerBar", "VetoQDCPerBar; veto channel; qdc ", 8, 0, 8, qdcbin, qdc_min, qdc_max)
Cosmic_VetoQdc = ROOT.TH1D("Cosmic_VetoQdc", "Cosmic_VetoQdc; veto channel; qdc ", qdcbin, qdc_min, qdc_max)
Cosmic_VetoQDCPerChannel = ROOT.TH2D("Cosmic_VetoQDCPerChannel", "Cosmic_VetoQDCPerChannel; veto channel; qdc ", DSn_bins, DSx_min, DSx_max, qdcbin, qdc_min, qdc_max)
Cosmic_VetoQDCPerBar = ROOT.TH2D("Cosmic_VetoQDCPerBar", "Cosmic_VetoQDCPerBar; veto channel; qdc ", 8, 0, 8, qdcbin, qdc_min, qdc_max)
Bkg_VetoQdc = ROOT.TH1D("Bkg_VetoQdc", "Bkg_VetoQdc; veto channel; qdc ", qdcbin, qdc_min, qdc_max)
Noise_VetoQdc = ROOT.TH1D("Noise_VetoQdc", "Noise_VetoQdc; veto channel; qdc ", qdcbin, qdc_min, qdc_max)

# Efficiency
V1BarEfficiency = ROOT.TEfficiency("V1BarEfficiency", "V1BarEfficiency; V1 bar; v3 efficiency", 7, 0, 7)
V2BarEfficiency = ROOT.TEfficiency("V2BarEfficiency", "V2BarEfficiency; V2 bar; v3 efficiency", 7, 0, 7)
Efficiency2D = ROOT.TEfficiency("Efficiency2D", "Efficiency2D; v1 bar; v2 bar", 7, 0, 7, 7, 0, 7)

ScifiEfficiency = ROOT.TEfficiency("ScifiEfficiency", "ScifiEfficiency; scifi x; scifi y", 1536, 0, 1536, 1536, 0, 1536)

#Alignment

V1_vs_V2 = ROOT.TH2D("V1_vs_V2", "V1_vs_V2; v1 bar; v2 bar", 7, 0, 7, 7, 0, 7)
V1_vs_V3 = ROOT.TH2D("V1_vs_V3", "V1_vs_V3; v1 bar; v3 bar", 7, 0, 7, 7, 0, 7)
V2_vs_V3 = ROOT.TH2D("V2_vs_V3", "V2_vs_V3; v2 bar; v3 bar", 7, 0, 7, 7, 0, 7)

V1_vs_scifi1x = ROOT.TH2D("V1_vs_scifi1x", "V1_vs_scifi1x; v1 channel; scifi1x channel", 7, 0, 7, 1536, 0, 1536)
V1_vs_scifi1y = ROOT.TH2D("V1_vs_scifi1y", "V1_vs_scifi1y; v1 channel; scifi1y channel", 7, 0, 7, 1536, 0, 1536)
V2_vs_scifi1x = ROOT.TH2D("V2_vs_scifi1x", "V2_vs_scifi1x; v2 channel; scifi1x channel", 7, 0, 7, 1536, 0, 1536)
V2_vs_scifi1y = ROOT.TH2D("V2_vs_scifi1y", "V2_vs_scifi1y; v2 channel; scifi1y channel", 7, 0, 7, 1536, 0, 1536)

###################
# loop on entries #
###################
vetoCounter = 0
scifiCounter = 0

Nentries = data.GetEntries()
for i in range(Nentries):
    entry = data.GetEntry(i)
    
    boardID = np.uint8(data.board_id)
    tofChannel = np.uint8(data.tofpet_channel)
    tofID = np.uint8(data.tofpet_id)
    qdc = np.asarray(data.value, float)

    scifi1xId = tofID[(boardID == 11) | (boardID == 17) | (boardID == 28)]
    scifi1xPin = tofChannel[(boardID == 11) | (boardID == 17) | ( boardID == 28)]
    scifi1xQdc = qdc[(boardID == 11) | (boardID == 17) | (boardID == 28)]

    scifi1yId = tofID[(boardID == 29) | (boardID == 3) | (boardID == 30)]
    scifi1yPin = tofChannel[(boardID == 29) | (boardID == 3) | (boardID == 30)]
    scifi1yQdc = qdc[(boardID == 29) | (boardID == 3) | (boardID == 30)]

    for v in scifi1xQdc: Scifi1xQdc.Fill(v)
    for v in scifi1yQdc: Scifi1yQdc.Fill(v)

    # first look at veto info before any cut
    v3Id = tofID[boardID == 48]
    v3Pin = tofChannel[boardID == 48]
    v3Qdc = qdc[boardID == 48]

    v3Multiplicity = len(v3Id)

    if v3Multiplicity > 0:        

        VetoHitMultiplicity.Fill(v3Multiplicity)

        v3Bars = [return_bar(mapVeto, v3Id[i], v3Pin[i]) for i in range(v3Multiplicity)]
        v3Ch = [return_ch(mapVeto, v3Id[i], v3Pin[i]) for i in range(v3Multiplicity)]

        v3BarQDC = np.full(8, -999)

        for i in range(v3Multiplicity):
                        
            VetoHits.Fill(v3Ch[i])
            VetoHitsperBar.Fill(v3Bars[i])
            if v3BarQDC[v3Bars[i]] == -999: v3BarQDC[v3Bars[i]] = v3Qdc[i]
            else : v3BarQDC[v3Bars[i]] += v3Qdc[i]
            VetoQdc.Fill(v3Qdc[i])
            VetoQDCPerChannel.Fill(v3Ch[i], v3Qdc[i])
        
        for i in v3Bars : VetoQDCPerBar.Fill(i, v3BarQDC[i])
    
    # get veto 1 and 2 events 
    vetoId = tofID[boardID == 58]
    vetoCh = tofChannel[boardID == 58]
    vetoQdc = qdc[boardID == 58]

    v1LId = vetoId[(vetoId<2)]
    v1RId = vetoId[(vetoId>5)]
    v2LId = vetoId[(vetoId>1) & (vetoId<4)]
    v2RId = vetoId[(vetoId>3) & (vetoId<6)]

    #############################
    # select cosmic rays events #
    #############################

    # ask Hits in left and right for both the first two veto planes
    if len(v1LId) > 0 and len(v1RId) > 0 and len(v2LId) > 0 and len(v2RId) > 0 :       
        
        v1LPin = vetoCh[(vetoId<2)]
        v1RPin = vetoCh[(vetoId>5)]
        v2LPin = vetoCh[(vetoId>1) & (vetoId<4)]
        v2RPin = vetoCh[(vetoId>3) & (vetoId<6)]

        v1LQdc = vetoQdc[(vetoId<2)]
        v1RQdc = vetoQdc[(vetoId>5)]
        v2LQdc = vetoQdc[(vetoId>1) & (vetoId<4)]
        v2RQdc = vetoQdc[(vetoId>3) & (vetoId<6)]

        v1LBars = [return_bar(mapVeto, v1LId[i], v1LPin[i]) for i in range(len(v1LId))]
        v1RBars = [return_bar(mapVeto, v1RId[i], v1RPin[i]) for i in range(len(v1RId))]
        v2LBars = [return_bar(mapVeto, v2LId[i], v2LPin[i]) for i in range(len(v2LId))]
        v2RBars = [return_bar(mapVeto, v2RId[i], v2RPin[i]) for i in range(len(v2RId))]
        
        v1RBarQDC = np.full(8, -999)
        for i in range(len(v1RId)) : 
            if v1RBarQDC[v1RBars[i]] == -999: v1RBarQDC[v1RBars[i]] = v1RQdc[i]
            else : v1RBarQDC[v1RBars[i]] += v1RQdc[i]
        
        v1LBarQDC = np.full(8, -999)
        for i in range(len(v1LId)) : 
            if v1LBarQDC[v1LBars[i]] == -999: v1LBarQDC[v1LBars[i]] = v1LQdc[i]
            else : v1LBarQDC[v1LBars[i]] += v1LQdc[i]

        v2RBarQDC = np.full(8, -999)
        for i in range(len(v2RId)) :
            if v2RBarQDC[v2RBars[i]] == -999: v2RBarQDC[v2RBars[i]] = v2RQdc[i]
            else : v2RBarQDC[v2RBars[i]] += v2RQdc[i]

        v2LBarQDC = np.full(8, -999)
        for i in range(len(v2LId)) : 
            if v2LBarQDC[v2LBars[i]] == -999: v2LBarQDC[v2LBars[i]] = v2LQdc[i]
            else : v2LBarQDC[v2LBars[i]] += v2LQdc[i]

        #study qdc of single hit events 
        if is_single_bar(v1LBars) and is_single_bar(v1RBars) and is_single_bar(v2RBars) and is_single_bar(v2LBars):
            
            v1LHitBar = (is_single_bar(v1LBars) - 1)
            v1RHitBar = (is_single_bar(v1RBars) - 1)
            v2LHitBar = (is_single_bar(v2LBars) - 1)
            v2RHitBar = (is_single_bar(v2RBars) - 1)

            v1LHitQdc = v1LBarQDC[v1LHitBar]
            v1RHitQdc = v1RBarQDC[v1RHitBar]
            v2LHitQdc = v2LBarQDC[v2LHitBar]
            v2RHitQdc = v2RBarQDC[v2RHitBar]

            V1LQdc_single.Fill(v1LHitQdc)
            V1RQdc_single.Fill(v1RHitQdc)
            V2LQdc_single.Fill(v2LHitQdc)
            V2RQdc_single.Fill(v2RHitQdc)

        #study qdc in events with noise and define the cosmic hit (max qdc value?)
        else :

            v1LHitQdc = np.max(v1LBarQDC)
            v1RHitQdc = np.max(v1RBarQDC)
            v2LHitQdc = np.max(v2LBarQDC)
            v2RHitQdc = np.max(v2RBarQDC)

            V1LQdc_max.Fill(v1LHitQdc)
            V1RQdc_max.Fill(v1RHitQdc)
            V2LQdc_max.Fill(v2LHitQdc)
            V2RQdc_max.Fill(v2RHitQdc)

            for v in v1LBarQDC: 
                if v != np.max(v1LBarQDC) : 
                    V1LQdc_others.Fill(v)
                    V1LQdc_residual.Fill(v1LHitQdc-v)

            for v in v1RBarQDC: 
                if v != np.max(v1RBarQDC) : 
                    V1RQdc_others.Fill(v)
                    V1RQdc_residual.Fill(v1RHitQdc-v)

            for v in v2LBarQDC: 
                if v != np.max(v2LBarQDC) : 
                    V2LQdc_others.Fill(v)
                    V2LQdc_residual.Fill(v2LHitQdc-v)

            for v in v2RBarQDC: 
                if v != np.max(v2RBarQDC) : 
                    V2RQdc_others.Fill(v)
                    V2RQdc_residual.Fill(v2RHitQdc-v)

            v1LHitBar = np.array(v1LBarQDC).argmax()
            v1RHitBar = np.array(v1RBarQDC).argmax()
            v2LHitBar = np.array(v2LBarQDC).argmax()
            v2RHitBar = np.array(v2RBarQDC).argmax()

        # fill hit histos
        for i in range(len(v1LId)) : 
            V1LHits.Fill(return_ch(mapVeto, v1LId[i], v1LPin[i]))
            V1LHitsperBar.Fill(v1LBars[i])

        for i in range(len(v1RId)) : 
            V1RHits.Fill(return_ch(mapVeto, v1RId[i], v1RPin[i]))
            V1RHitsperBar.Fill(v1RBars[i])
            
        for i in range(len(v2LId)) : 
            V2LHits.Fill(return_ch(mapVeto, v2LId[i], v2LPin[i]))
            V2LHitsperBar.Fill(v2LBars[i])
            
        for i in range(len(v2RId)) : 
            V2RHits.Fill(return_ch(mapVeto, v2RId[i], v2RPin[i]))
            V2RHitsperBar.Fill(v2RBars[i])


        # ask for same bar Hit in left and right
        if v1LHitBar == v1RHitBar and v2LHitBar == v2RHitBar:
            
            V1LQdc.Fill(v1LHitQdc)
            V1RQdc.Fill(v1RHitQdc)
            V2LQdc.Fill(v2LHitQdc)
            V2RQdc.Fill(v2RHitQdc)

            V1QdcDiff.Fill(v1RHitQdc - v1LHitQdc)
            V2QdcDiff.Fill(v2RHitQdc - v2LHitQdc)

            V1_vs_V2.Fill(v1LHitBar, v2LHitBar)

            # cut on qdc signal per bar 

            if v1LHitQdc > 0 and v1RHitQdc > 0 and v2RHitQdc > 0 and v2LHitQdc > 0 :
                
                # fill veto 3 plots in cosmic events
                if v3Multiplicity > 0:
                    v3BarQDC = np.full(8, -999)
                    for i in range(v3Multiplicity):
                        
                        Cosmic_VetoHits.Fill(v3Ch[i])
                        Cosmic_VetoHitsperBar.Fill(v3Bars[i])
                        Cosmic_VetoQdc.Fill(v3Qdc[i])
                        Cosmic_VetoQDCPerChannel.Fill(v3Ch[i], v3Qdc[i])
                        v3BarQDC[v3Bars[i]] += v3Qdc[i]
                    
                    for i in v3Bars :
                        Cosmic_VetoQDCPerBar.Fill(i, v3BarQDC[i])
                        V1_vs_V3.Fill(v1LHitBar, i)
                        V2_vs_V3.Fill(v2LHitBar, i)

                if abs(v1LHitBar-v2LHitBar) < 2 : 
                    vetoCounter+=1
                    V1BarEfficiency.Fill((v3Multiplicity > 0), v1LHitBar)
                    V2BarEfficiency.Fill((v3Multiplicity > 0), v2LHitBar)
                    Efficiency2D.Fill((v3Multiplicity > 0), v1LHitBar, v2LHitBar)

                if len(scifi1xId) > 0  and len(scifi1yId) > 0 :
                        
                        scifiCounter +=1 
                        scifi1xHitCh = [scifi1xId[i]*64 + 63 - scifi1xPin[i] for i in range(len(scifi1xId))]
                        scifi1yHitCh = [scifi1yId[i]*64 + 63 - scifi1yPin[i] for i in range(len(scifi1yId))]

                        for i in scifi1xHitCh : 
                            V1_vs_scifi1x.Fill(v1LHitBar, i)
                            V2_vs_scifi1x.Fill(v2LHitBar, i)
                        for i in scifi1yHitCh :
                            V1_vs_scifi1y.Fill(v1LHitBar, i)
                            V2_vs_scifi1y.Fill(v2LHitBar, i)
            
############################
# write histo to root file #
############################

V1LQdc.Write()
V1RQdc.Write()
V2LQdc.Write()
V2RQdc.Write()
Scifi1xQdc.Write()
Scifi1yQdc.Write()

V1QdcDiff.Write()
V2QdcDiff.Write()

V1_vs_V2.Write()
V1_vs_V3.Write()
V2_vs_V3.Write()
V1_vs_scifi1x.Write()
V1_vs_scifi1y.Write()
V2_vs_scifi1x.Write()
V2_vs_scifi1y.Write()

V1LHits.Write()
V1LHitsperBar.Write()
V1RHits.Write()
V1RHitsperBar.Write()
V2LHits.Write()
V2LHitsperBar.Write()
V2RHits.Write()
V2RHitsperBar.Write()

V1LQdc_max.Write()
V1LQdc_others.Write()
V1LQdc_single.Write()
V1LQdc_residual.Write()

V1RQdc_max.Write()
V1RQdc_others.Write()
V1RQdc_single.Write()
V1RQdc_residual.Write()

V2LQdc_max.Write()
V2LQdc_others.Write()
V2LQdc_single.Write()
V2LQdc_residual.Write()

V2RQdc_max.Write()
V2RQdc_others.Write()
V2RQdc_single.Write()
V2RQdc_residual.Write()

V1BarEfficiency.Write()
V2BarEfficiency.Write()
Efficiency2D.Write()

VetoHits.Write()
VetoHitsperBar.Write()
VetoQdc.Write()
VetoQDCPerChannel.Write()
VetoQDCPerBar.Write()

Cosmic_VetoHits.Write()
Cosmic_VetoHitsperBar.Write()
Cosmic_VetoQdc.Write()
Cosmic_VetoQDCPerChannel.Write()
Cosmic_VetoQDCPerBar.Write()

outfile.Close()

print(f'Entries {Nentries} with {vetoCounter} cosmic veto events of which {scifiCounter} also have scifi. \nRatio of veto cosmics {vetoCounter/Nentries}, plus scifi {scifiCounter/Nentries} ')