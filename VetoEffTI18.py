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
            return int(row[0])
    return DEFAULT

def return_bar(map, tofpet_id, tofpet_channel):    
    for row in map:
        if (row[4] == str(tofpet_channel) and row[3] == str(tofpet_id%2)):
            if int(np.floor((int(row[0])-1)/8)) == 7 : print('nope')
            return int(np.floor((int(row[0])-1)/8))
        
    return DEFAULT

def is_single_bar(list):
    if all(i == list[0] for i in list) :
        return int(list[0])+1
    else : 
        return 0

# scifi 1x [11,17,28] 1y [29,3,30]

scifi_map = {
    "11" : 0, #scifi1x
    "17" : 1, 
    "28" : 2, 
    "29" : 0, #scifi1y
    "3"  : 1, 
    "30" : 2, 
    "23" : 0, #scifi2x
    "2"  : 1, 
    "25" : 2,
    "16" : 0, #scifi2y
    "14" : 1,
    "18" : 2
}

DEFAULT = -999
LIGHTPROP = 15 #cm/ns
HALFBAR = 42/2 #half veto bar
EMULSIONDIM = 10 #cm
VETODISTANCE = 3
SCIFICUT = 1 #cm 

#############
# read data #
#############

runN = sys.argv[1]
runDirectory = f"/eos/experiment/sndlhc/raw_data/physics/2024/ecc_run_06/run_00{runN}/"
if not os.path.exists(runDirectory): sys.exit(1)

data = ROOT.TChain("data")

filelist = glob(f"{runDirectory}data_*.root")
if len(filelist) == 0: sys.exit(1)

for file in filelist:
    data.Add(file)

# read mapping cvs
mapVeto = read_csv_file("./SiPMmaps/Veto_SiPM_mapping.csv")

#prepare output file
filename = f"./results/runs/collisions/output_run{runN}.root"
outfile = ROOT.TFile.Open(filename, "RECREATE")

#################
# Define histos #
#################

DSn_bins = 58
DSx_min = -.5
DSx_max = 57.5

nbar = 7
bar_min = -0.5
bar_max = 6.5
scifich = 512*3
scifidim = 39
scifi_min = -0.5 
scifi_max = 38.5
vetobin = 43
veto_min = -.5
veto_max = 42.5


# Hits info 
V2LHits = ROOT.TH1D("V2LHits", "V2 L Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
V2LHitsperBar = ROOT.TH1D("V2LHitsperBar", "V2 L Hits per Bar; veto bar; entries", nbar, bar_min, bar_max)
V2RHits = ROOT.TH1D("V2RHits", "V2 R Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
V2RHitsperBar = ROOT.TH1D("V2RHitsperBar", "V2 R Hits per Bar; veto bar; entries", nbar, bar_min, bar_max)
VetoHits = ROOT.TH1D("VetoHits", "Veto Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
VetoHitsperBar = ROOT.TH1D("VetoHitsperBar", "Veto Hits per Bar; veto bar; entries", nbar, bar_min, bar_max)
VetoHitMultiplicity = ROOT.TH1D("VetoHitMultiplicity", "Veto Hit Multiplicity;  Hits per event; entries", 20, -.5, 19.5)

Cosmic_V2HitsperBar = ROOT.TH1D("Cosmic_V2HitsperBar", "Cosmic Veto 2 Hits perBar; bar; entries", nbar, bar_min, bar_max)
Cosmic_VetoHits = ROOT.TH1D("Cosmic_VetoHits", "Veto Hits in cosmics events;  veto channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitsperBar = ROOT.TH1D("Cosmic_VetoHitsperBar", "Cosmic_Veto Hits per Bar; veto channel; entries", nbar, bar_min, bar_max)

Bkg_VetoHits = ROOT.TH1D("Bkg_VetoHits", "Veto Hits far from expectedX position;  veto bar; entries", nbar, 0, nbar)
Bkg_VetoMultiplicity = ROOT.TH1D("Bkg_VetoMultiplicity", "Veto Hits far from expectedX position;  n veto hits; entries", 20, -.5, 19.5)
Bkg_VetoBarMultiplicity = ROOT.TH1D("Bkg_VetoBarMultiplicity", "Veto Hits far from expectedX position;  n veto bars; entries", 8, -.5, 7.5)

# qdc
qdc_min = -20
qdc_max = 400
qdcbin = qdc_max - qdc_min

Scifi1xQdc = ROOT.TH1D("Scifi1xQdc", "Scifi1xQdc; qdc; entries", 100, -24.5, 25.5)
Scifi1yQdc = ROOT.TH1D("Scifi1yQdc", "Scifi1yQdc; qdc; entries", 100, -24.5, 25.5)
Scifi1xQdc_max = ROOT.TH1D("Scifi1xQdc_max", "Scifi1xQdc_max; qdc_max; entries", 100, -24.5, 25.5)
Scifi1yQdc_max = ROOT.TH1D("Scifi1yQdc_max", "Scifi1yQdc_max; qdc_max; entries", 100, -24.5, 25.5)
Scifi1xQdc_others = ROOT.TH1D("Scifi1xQdc_others", "Scifi1xQdc_others; qdc_others; entries", 100, -24.5, 25.5)
Scifi1yQdc_others = ROOT.TH1D("Scifi1yQdc_others", "Scifi1yQdc_others; qdc_others; entries", 100, -24.5, 25.5)
Scifi1xQdc_residual = ROOT.TH1D("Scifi1xQdc_residual", "Scifi1xQdc_residual; qdc max - others; entries", 70, 0, 70)
Scifi1yQdc_residual = ROOT.TH1D("Scifi1yQdc_residual", "Scifi1yQdc_residual; qdc max - others; entries", 70, 0, 70)

Scifi1xPos_diff = ROOT.TH1D("Scifi1xPos_diff", "Scifi1xPos_diff; Pos qdc max - others; entries", 160, -20, 20)
Scifi1yPos_diff = ROOT.TH1D("Scifi1yPos_diff", "Scifi1yPos_diff; Pos qdc max - others; entries", 160, -20, 20)

V2LQdc = ROOT.TH1D("V2LQdc", "V2LQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQdc = ROOT.TH1D("V2RQdc", "V2RQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQDCPerBar = ROOT.TH2D("V2RQDCPerBar", "V2RQDCPerBar; v2 R channel; qdc ", nbar, bar_min, bar_max, qdcbin, qdc_min, qdc_max)
V2LQDCPerBar = ROOT.TH2D("V2LQDCPerBar", "V2LQDCPerBar; v2 L channel; qdc ", nbar, bar_min, bar_max, qdcbin, qdc_min, qdc_max)

VetoQdc = ROOT.TH1D("VetoQdc", "VetoQdc; qdc; entries", 100, -10, 40)
VetoQDCPerChannel = ROOT.TH2D("VetoQDCPerChannel", "VetoQDCPerChannel; veto channel; qdc ", DSn_bins, DSx_min, DSx_max, qdcbin, qdc_min, qdc_max)
VetoQDCPerBar = ROOT.TH2D("VetoQDCPerBar", "VetoQDCPerBar; veto channel; qdc ", nbar, bar_min, bar_max, qdcbin, qdc_min, qdc_max)
Cosmic_VetoQdc = ROOT.TH1D("Cosmic_VetoQdc", "Cosmic_VetoQdc; veto channel; qdc ", qdcbin, qdc_min, qdc_max)
Cosmic_VetoQDCPerChannel = ROOT.TH2D("Cosmic_VetoQDCPerChannel", "Cosmic_VetoQDCPerChannel; veto channel; qdc ", DSn_bins, DSx_min, DSx_max, qdcbin, qdc_min, qdc_max)
Cosmic_VetoQDCPerBar = ROOT.TH2D("Cosmic_VetoQDCPerBar", "Cosmic_VetoQDCPerBar; veto channel; qdc ", nbar, bar_min, bar_max, qdcbin, qdc_min, qdc_max)
Bkg_VetoQdc = ROOT.TH1D("Bkg_VetoQdc", "Bkg_VetoQdc; veto channel; qdc ", qdcbin, qdc_min, qdc_max)

#Alignment
Scifi1Pos = ROOT.TH2D("Scifi1Pos", "Scifi1Pos; scifi1x; scifi1y", scifidim, scifi_min, scifi_max, scifidim, scifi_min, scifi_max)
Scifi2Pos = ROOT.TH2D("Scifi2Pos", "Scifi2Pos; scifi2x; scifi2y", scifidim, scifi_min, scifi_max, scifidim, scifi_min, scifi_max)

V2_vs_V3 = ROOT.TH2D("V2_vs_V3", "V2_vs_V3; v2 bar; v3 bar", nbar, bar_min, bar_max, nbar, bar_min, bar_max)
V2L_vs_V2R = ROOT.TH2D("V2L_vs_V2R", "V2L_vs_V2R; v2 L; v3 R", nbar, bar_min, bar_max, nbar, bar_min, bar_max)
V2_vs_scifi1x = ROOT.TH2D("V2_vs_scifi1x", "V2_vs_scifi1x; v2 bar; scifi1x channel", nbar, bar_min, bar_max, scifidim, scifi_min, scifi_max)
V2_vs_scifi1y = ROOT.TH2D("V2_vs_scifi1y", "V2_vs_scifi1y; v2 bar; scifi1y channel", nbar, bar_min, bar_max, scifidim, scifi_min, scifi_max)
V2_vs_scifi2x = ROOT.TH2D("V2_vs_scifi2x", "V2_vs_scifi2x; v2 bar; scifi2x channel", nbar, bar_min, bar_max, scifidim, scifi_min, scifi_max)
V2_vs_scifi2y = ROOT.TH2D("V2_vs_scifi2y", "V2_vs_scifi2y; v2 bar; scifi2y channel", nbar, bar_min, bar_max, scifidim, scifi_min, scifi_max)
V3_vs_scifi1x = ROOT.TH2D("V3_vs_scifi1x", "V3_vs_scifi1x; v3 bar; scifi1x channel", nbar, bar_min, bar_max, scifidim, scifi_min, scifi_max)
V3_vs_scifi1y = ROOT.TH2D("V3_vs_scifi1y", "V3_vs_scifi1y; v3 bar; scifi1y channel", nbar, bar_min, bar_max, scifidim, scifi_min, scifi_max)

DeltaX_Distribution = ROOT.TH1D("DeltaX_Distribution", "DeltaX_Distribution; Dx; Entries", 51, -25.5, 25.5)
DeltaY_Distribution = ROOT.TH1D("DeltaY_Distribution", "DeltaY_Distribution; Dy; Entries", 51, -25.5, 25.5)

ExpectedBarV3Residual = ROOT.TH1D("ExpectedBarV3Residual", "ExpectedBarV3Residual; expected bar from scifi1 and 2 - v3 hit bar; entries", 17, -8.5, 8.5)
ExpectedPos = ROOT.TH2D("ExpectedPos", "ExpectedPos using scifi 1 and scifi 2; expected x ; expected y", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
ExpectedPosX = ROOT.TH1D("ExpectedPosX", "ExpectedPos using scifi 1 and scifi 2; expected x ; entries", vetobin, veto_min, veto_max)
ExpectedPosY = ROOT.TH1D("ExpectedPosY", "ExpectedPos using scifi 1 and scifi 2; expected x ; entries", vetobin, veto_min, veto_max)

# Efficiency
Denominator_straightMu = ROOT.TH2D("Denominator_straightMu", "Denominator_straightMu; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Numerator_straightMu = ROOT.TH2D("Numerator_straightMu", "Numerator_straightMu; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Denominator_CR = ROOT.TH2D("Denominator_CR", "Denominator_CR; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Numerator_CR = ROOT.TH2D("Numerator_CR", "Numerator_CR; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)

Efficiency = ROOT.TEfficiency("Efficiency", "Efficiency; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Efficiency_straightMu = ROOT.TEfficiency("Efficiency_straightMu", "Efficiency_straightMu; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Efficiency_CR = ROOT.TEfficiency("Efficiency_CR", "Efficiency_CR; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Efficiency_dyge0 = ROOT.TEfficiency("Efficiency_dyge0", "Efficiency_dyge0; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Efficiency_dyl0 = ROOT.TEfficiency("Efficiency_dyl0", "Efficiency_dyl0; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Efficiency_dxge0 = ROOT.TEfficiency("Efficiency_dxge0", "Efficiency_dxge0; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
Efficiency_dxl0 = ROOT.TEfficiency("Efficiency_dxl0", "Efficiency_dxl0; expected position x (cm) ; expected position y (cm)", vetobin, veto_min, veto_max, vetobin, veto_min, veto_max)
EfficiencyX = ROOT.TEfficiency("EfficiencyX", "Efficiency x; expected x (cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyBarX = ROOT.TEfficiency("EfficiencyBarX", "Efficiency x; expected bar; efficiency", nbar, bar_min, bar_max)
EfficiencyY = ROOT.TEfficiency("EfficiencyY", "Efficiency y; expected y(cm); efficiency", vetobin, veto_min, veto_max)
Efficiency_dx = ROOT.TEfficiency("Efficiencydx", "Efficiency dx; expected x (cm); efficiency", 51, -25.5, 25.5)
Efficiency_dy = ROOT.TEfficiency("Efficiencydy", "Efficiency dy; expected x (cm); efficiency", 51, -25.5, 25.5)

EfficiencyY_Bar0 = ROOT.TEfficiency("EfficiencyY_Bar0", "Efficiency y_Bar0; expected y(cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyY_Bar1 = ROOT.TEfficiency("EfficiencyY_Bar1", "Efficiency y_Bar1; expected y(cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyY_Bar2 = ROOT.TEfficiency("EfficiencyY_Bar2", "Efficiency y_Bar2; expected y(cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyY_Bar3 = ROOT.TEfficiency("EfficiencyY_Bar3", "Efficiency y_Bar3; expected y(cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyY_Bar4 = ROOT.TEfficiency("EfficiencyY_Bar4", "Efficiency y_Bar4; expected y(cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyY_Bar5 = ROOT.TEfficiency("EfficiencyY_Bar5", "Efficiency y_Bar5; expected y(cm); efficiency", vetobin, veto_min, veto_max)
EfficiencyY_Bar6 = ROOT.TEfficiency("EfficiencyY_Bar6", "Efficiency y_Bar6; expected y(cm); efficiency", vetobin, veto_min, veto_max)

Close_vs_farEfficiency = ROOT.TEfficiency( "Close_vs_farEfficiency", "Close_vs_farEfficiency", 7 , 0, 7)
Close_vs_farEfficiency_Bar0 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar0", "Close_vs_farEfficiency_Bar0", 7, 0, 7)
Close_vs_farEfficiency_Bar1 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar1", "Close_vs_farEfficiency_Bar1", 7, 0, 7)
Close_vs_farEfficiency_Bar2 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar2", "Close_vs_farEfficiency_Bar2", 7, 0, 7)
Close_vs_farEfficiency_Bar3 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar3", "Close_vs_farEfficiency_Bar3", 7, 0, 7)
Close_vs_farEfficiency_Bar4 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar4", "Close_vs_farEfficiency_Bar4", 7, 0, 7)
Close_vs_farEfficiency_Bar5 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar5", "Close_vs_farEfficiency_Bar5", 7, 0, 7)
Close_vs_farEfficiency_Bar6 = ROOT.TEfficiency ( "Close_vs_farEfficiency_Bar6", "Close_vs_farEfficiency_Bar6", 7, 0, 7)

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
    time = np.asanyarray(data.timestamp, float)

    scifi1xBoard = boardID[(boardID == 11) | (boardID == 17) | (boardID == 28)]
    scifi1xId = tofID[(boardID == 11) | (boardID == 17) | (boardID == 28)]
    scifi1xPin = tofChannel[(boardID == 11) | (boardID == 17) | ( boardID == 28)]
    scifi1xQdc = qdc[(boardID == 11) | (boardID == 17) | (boardID == 28)]

    scifi1yBoard = boardID[(boardID == 29) | (boardID == 3) | (boardID == 30)]
    scifi1yId = tofID[(boardID == 29) | (boardID == 3) | (boardID == 30)]
    scifi1yPin = tofChannel[(boardID == 29) | (boardID == 3) | (boardID == 30)]
    scifi1yQdc = qdc[(boardID == 29) | (boardID == 3) | (boardID == 30)]

    scifi2xBoard = boardID[(boardID == 23) | (boardID == 2) | (boardID == 25)]  #23,2,25
    scifi2xId = tofID[(boardID == 23) | (boardID == 2) | (boardID == 25)]
    scifi2xPin = tofChannel[(boardID == 23) | (boardID == 2) | ( boardID == 25)]
    scifi2xQdc = qdc[(boardID == 23) | (boardID == 2) | (boardID == 25)]
    
    scifi2yBoard = boardID[(boardID == 16) | (boardID == 14) | (boardID == 18)]  #16,14,18
    scifi2yId = tofID[(boardID == 16) | (boardID == 14) | (boardID == 18)]
    scifi2yPin = tofChannel[(boardID == 16) | (boardID == 14) | ( boardID == 18)]
    scifi2yQdc = qdc[(boardID == 16) | (boardID == 14) | (boardID == 18)]

    for v in scifi1xQdc: Scifi1xQdc.Fill(v)
    for v in scifi1yQdc: Scifi1yQdc.Fill(v)

    # first look at veto info before any cut
    v3Id = tofID[boardID == 48]
    v3Pin = tofChannel[boardID == 48]
    v3Qdc = qdc[boardID == 48]

    v3Multiplicity = len(v3Id)
    v3BarMultiplicity = 0

    if v3Multiplicity > 0:        

        VetoHitMultiplicity.Fill(v3Multiplicity)

        v3Bars = [return_bar(mapVeto, v3Id[i], v3Pin[i]) for i in range(v3Multiplicity)]
        v3Ch = [return_ch(mapVeto, v3Id[i], v3Pin[i]) for i in range(v3Multiplicity)]

        v3BarQDC = np.full(7, DEFAULT)

        for i in range(v3Multiplicity):
                        
            VetoHits.Fill(v3Ch[i])
            VetoHitsperBar.Fill(v3Bars[i])
            if v3BarQDC[v3Bars[i]] == DEFAULT: v3BarQDC[v3Bars[i]] = v3Qdc[i]
            else : v3BarQDC[v3Bars[i]] += v3Qdc[i]
            VetoQdc.Fill(v3Qdc[i])
            VetoQDCPerChannel.Fill(v3Ch[i], v3Qdc[i])
        
        for i in v3Bars : VetoQDCPerBar.Fill(i, v3BarQDC[i])
    
        v3BarMultiplicity = (v3BarQDC > DEFAULT).sum()
    
    # get veto 1 and 2 events 
    vetoId = tofID[boardID == 58]
    vetoCh = tofChannel[boardID == 58]
    vetoQdc = qdc[boardID == 58]
    vetoTime = time[boardID == 58]

    v2LId = vetoId[(vetoId>1) & (vetoId<4)]         # B: 2-3
    v2RId = vetoId[(vetoId>3) & (vetoId<6)]         # C: 4-5

    #############################
    # select cosmic rays events #
    #############################

    # ask Hits in left and right for v2
    if len(v2LId) > 0 and len(v2RId) > 0 :      

        v2LTime =vetoTime[(vetoId>1) & (vetoId<4)]
        v2RTime =vetoTime[(vetoId>3) & (vetoId<6)]
        
        v2LPin = vetoCh[(vetoId>1) & (vetoId<4)]
        v2RPin = vetoCh[(vetoId>3) & (vetoId<6)]

        v2LQdc = vetoQdc[(vetoId>1) & (vetoId<4)]
        v2RQdc = vetoQdc[(vetoId>3) & (vetoId<6)]

        v2LBars = [return_bar(mapVeto, v2LId[i], v2LPin[i]) for i in range(len(v2LId))]
        v2RBars = [return_bar(mapVeto, v2RId[i], v2RPin[i]) for i in range(len(v2RId))]
        
        for bL in v2LBars:
            for bR in v2RBars: V2L_vs_V2R.Fill(bL, bR)

        # fill hit histos            
        for i in range(len(v2LId)) : 
            V2LHits.Fill(return_ch(mapVeto, v2LId[i], v2LPin[i]))
            V2LHitsperBar.Fill(v2LBars[i])
            
        for i in range(len(v2RId)) : 
            V2RHits.Fill(return_ch(mapVeto, v2RId[i], v2RPin[i]))
            V2RHitsperBar.Fill(v2RBars[i])


        #study qdc
        v2RBarQDC = np.full(7, DEFAULT)
        for i in range(len(v2RId)) :
            if v2RBarQDC[v2RBars[i]] == DEFAULT: v2RBarQDC[v2RBars[i]] = v2RQdc[i]
            else : v2RBarQDC[v2RBars[i]] += v2RQdc[i]

        v2LBarQDC = np.full(7, DEFAULT)
        for i in range(len(v2LId)) : 
            if v2LBarQDC[v2LBars[i]] == DEFAULT: v2LBarQDC[v2LBars[i]] = v2LQdc[i]
            else : v2LBarQDC[v2LBars[i]] += v2LQdc[i]

        for i in range(7):
            if v2RBarQDC[i] != DEFAULT : V2RQDCPerBar.Fill(i, v2RBarQDC[i])
            if v2LBarQDC[i] != DEFAULT : V2LQDCPerBar.Fill(i, v2LBarQDC[i])
 
        #study qdc of single hit events 
        if is_single_bar(v2RBars) and is_single_bar(v2LBars):
            
            v2LHitBar = (is_single_bar(v2LBars) - 1)
            v2RHitBar = (is_single_bar(v2RBars) - 1)

            v2LHitQdc = v2LBarQDC[v2LHitBar]
            v2RHitQdc = v2RBarQDC[v2RHitBar]

        #study qdc in events with noise and define the cosmic hit (max qdc value?)
        else :

            v2LHitQdc = np.max(v2LBarQDC)
            v2RHitQdc = np.max(v2RBarQDC)

            v2LHitBar = np.array(v2LBarQDC).argmax()
            v2RHitBar = np.array(v2RBarQDC).argmax()
            
        # ask for veto 2 and scifi 1 -> must have passed through v3
        if is_single_bar(v2RBars) and is_single_bar(v2LBars) and v2LHitBar == v2RHitBar and len(scifi1xId) > 0 and len(scifi1yId) > 0 :
            
            V2LQdc.Fill(v2LHitQdc)
            V2RQdc.Fill(v2RHitQdc)
    
            scifi1xHitCh = [scifi_map[str(scifi1xBoard[i])]*512 + scifi1xId[i]*64 + 63 - scifi1xPin[i] for i in range(len(scifi1xId))]
            scifi1yHitCh = [scifi_map[str(scifi1yBoard[i])]*512 + scifi1yId[i]*64 + 63 - scifi1yPin[i] for i in range(len(scifi1yId))]

            scifi1xHitPos = [scifi1xHitCh[i]*0.025 for i in range(len(scifi1xId))]
            scifi1yHitPos = [scifi1yHitCh[i]*0.025 for i in range(len(scifi1yId))]
            
            #find position of scifi hit
            # if there's exactly one easy
            if len(scifi1xId) == 1 and len(scifi1yId) == 1 : 
                scifi1xHit = scifi1xHitPos[0]
                scifi1yHit = scifi1yHitPos[0]
                Scifi1Pos.Fill(scifi1xHit, scifi1yHit)

            # if there's more cluster around the max qdc   
            else :
                scifi1xQdcMax = np.max(scifi1xQdc)
                scifi1yQdcMax = np.max(scifi1yQdc)

                Scifi1xQdc_max.Fill(scifi1xQdcMax)
                Scifi1yQdc_max.Fill(scifi1yQdcMax)
                
                for v in scifi1xQdc :
                    if v != scifi1xQdcMax : 
                        Scifi1xQdc_residual.Fill(scifi1xQdcMax - v)
                        Scifi1xQdc_others.Fill(v)
                
                for v in scifi1yQdc:
                    if v != scifi1yQdcMax : 
                        Scifi1yQdc_residual.Fill(scifi1yQdcMax - v)
                        Scifi1yQdc_others.Fill(v)

                scifi1xPosMax = scifi1xHitPos[np.array(scifi1xQdc).argmax()]
                scifi1yPosMax = scifi1yHitPos[np.array(scifi1yQdc).argmax()]

                #cluster closeby hits and taka average as position
                scifi1xPosCloseby = []
                scifi1yPosCloseby = []
                scifi1xPosCloseby.append(scifi1xPosMax)
                scifi1yPosCloseby.append(scifi1yPosMax)

                for p in scifi1xHitPos: 
                    if p != scifi1xPosMax :
                        diff = scifi1xPosMax - p
                        Scifi1xPos_diff.Fill(diff)
                        if abs(diff) <= SCIFICUT : scifi1xPosCloseby.append(p)
                
                for p in scifi1yHitPos:
                    if p != scifi1yPosMax :
                        diff = scifi1yPosMax - p
                        Scifi1yPos_diff.Fill(diff)
                        if abs(diff) <= SCIFICUT : scifi1yPosCloseby.append(p)

                if ( len(scifi1yPosCloseby)-len(scifi1yId) ) != 0 or ( len(scifi1xPosCloseby)-len(scifi1xId) ) != 0  :
                    continue

                scifi1xHit = sum(scifi1xPosCloseby)/float(len(scifi1xPosCloseby))
                scifi1yHit = sum(scifi1yPosCloseby)/float(len(scifi1yPosCloseby))
                                    
            Scifi1Pos.Fill(scifi1xHit, scifi1yHit)
            
            V2_vs_scifi1x.Fill(v2LHitBar, scifi1xHit)
            for b in v3Bars : V3_vs_scifi1x.Fill(b, scifi1xHit)

            V2_vs_scifi1y.Fill(v2LHitBar, scifi1yHit)
            for b in v3Bars : V3_vs_scifi1y.Fill(b, scifi1yHit)
            
            # ask also scifi 2 
            if len(scifi2xId) > 0 and len(scifi2yId) > 0 : 

                # fill veto 3 plots in cosmic events
                if v3Multiplicity > 0:
                    for i in range(v3Multiplicity):
                    
                        Cosmic_VetoHits.Fill(v3Ch[i])
                        Cosmic_VetoHitsperBar.Fill(v3Bars[i])
                        Cosmic_VetoQdc.Fill(v3Qdc[i])
                        Cosmic_VetoQDCPerChannel.Fill(v3Ch[i], v3Qdc[i])
                    
                    for i in v3Bars :
                        V2_vs_V3.Fill(v2LHitBar, i)
                    
                    for i in v3Bars : 
                        if v3BarQDC[i] != DEFAULT : 
                            Cosmic_VetoQDCPerBar.Fill(i, v3BarQDC[i])

                v3HitBar = np.array(v3BarQDC).argmax() if max(v3BarQDC) != DEFAULT else DEFAULT

                # check cosmic distribution in V2 bars
                Cosmic_V2HitsperBar.Fill(v2LHitBar)

                #find position for scifi 2 hit
                scifi2xHitCh = [scifi_map[str(scifi2xBoard[i])]*512 + scifi2xId[i]*64 + 63 - scifi2xPin[i] for i in range(len(scifi2xId))]
                scifi2yHitCh = [scifi_map[str(scifi2yBoard[i])]*512 + scifi2yId[i]*64 + 63 - scifi2yPin[i] for i in range(len(scifi2yId))]
                
                scifi2xHitPos = [scifi2xHitCh[i]*0.025 for i in range(len(scifi2xId))]
                scifi2yHitPos = [scifi2yHitCh[i]*0.025 for i in range(len(scifi2yId))]
                
                if len(scifi2xId) == 1 and len(scifi2yId) == 1 : 
                    scifi2xHit = scifi2xHitPos[0]
                    scifi2yHit = scifi2yHitPos[0]

                # if there's more, cluster-> if more than one I can't say anything
                else :
                    scifi2xQdcMax = np.max(scifi2xQdc)
                    scifi2yQdcMax = np.max(scifi2yQdc)

                    scifi2xPosMax = scifi2xHitPos[np.array(scifi2xQdc).argmax()]
                    scifi2yPosMax = scifi2yHitPos[np.array(scifi2yQdc).argmax()]

                    #cluster closeby hits and taka average as position
                    scifi2xPosCloseby = []
                    scifi2yPosCloseby = []
                    scifi2xPosCloseby.append(scifi2xPosMax)
                    scifi2yPosCloseby.append(scifi2yPosMax)

                    for p in scifi2xHitPos: 
                        if p != scifi2xPosMax :
                            diff = scifi2xPosMax - p
                            if abs(diff) <= SCIFICUT : scifi2xPosCloseby.append(p)
                    
                    for p in scifi2yHitPos:
                        if p != scifi2yPosMax :
                            diff = scifi2yPosMax - p
                            if abs(diff) <= SCIFICUT : scifi2yPosCloseby.append(p)
                   
                    if ( len(scifi2yPosCloseby)-len(scifi2yId) ) != 0 or ( len(scifi2xPosCloseby)-len(scifi2xId) ) != 0  :
                        continue

                    scifi2xHit = sum(scifi2xPosCloseby)/float(len(scifi2xPosCloseby))
                    scifi2yHit = sum(scifi2yPosCloseby)/float(len(scifi2yPosCloseby))
                
                Scifi2Pos.Fill(scifi2xHit, scifi2yHit)
                V2_vs_scifi2x.Fill(v2LHitBar, scifi2xHit)
                V2_vs_scifi2y.Fill(v2LHitBar, scifi2yHit)
                
                dy = (scifi1yHit - scifi2yHit)
                dx = (scifi1xHit - scifi2xHit)
                v3yExpectedPos = scifi1yHit + dy
                v3xExpectedPos = scifi1xHit + dx
                
                ExpectedPos.Fill(v3xExpectedPos, v3yExpectedPos)
                ExpectedPosX.Fill(v3xExpectedPos)
                ExpectedPosY.Fill(v3yExpectedPos)

                expectedXBar = int(np.floor(v3xExpectedPos/6))
                expectedYBar = int(np.floor(v3yExpectedPos/6))

                compatibleV2 = False

                if (expectedYBar == 0 and (v2RBarQDC[expectedYBar] != DEFAULT or v2RBarQDC[expectedYBar+1] != DEFAULT) ) : compatibleV2 = True
                elif ( expectedYBar == 6 and (v2RBarQDC[expectedYBar] != DEFAULT or v2RBarQDC[expectedYBar-1] != DEFAULT) ) : compatibleV2 = True                           
                elif ( (expectedYBar > 0  and expectedYBar < 6) and (v2RBarQDC[expectedYBar] != DEFAULT or v2RBarQDC[expectedYBar-1] != DEFAULT or v2RBarQDC[expectedYBar+1] != DEFAULT) ) : compatibleV2 = True          

                # if (scifi1yHit - scifi2yHit) > 0 : # dal basso verso l'alto
                #     compatibleV2 = (v3yExpectedPos <= (v2LHitBar*6))
                # else :
                #     compatibleV2 = (v3yExpectedPos >= (v2LHitBar*6))
                
                # print(v3xExpectedPos, v3yExpectedPos, (v2LHitBar*6), (scifi1yHit - scifi2yHit), compatibleV2)

                ExpectedBarV3Residual.Fill(v3HitBar - int(np.floor(v3xExpectedPos/6)) )

                if v3xExpectedPos >= 0 and v3xExpectedPos <= 42 and v3yExpectedPos >= 0 and v3yExpectedPos <= 42 and compatibleV2:

                    DeltaX_Distribution.Fill(dy)
                    DeltaY_Distribution.Fill(dx)

                    v3hit = False
                    
                    if (expectedXBar == 0 and (v3BarQDC[expectedXBar] != DEFAULT or v3BarQDC[expectedXBar+1] != DEFAULT) ) : v3hit = True
                    elif ( expectedXBar == 6 and (v3BarQDC[expectedXBar] != DEFAULT or v3BarQDC[expectedXBar-1] != DEFAULT) ) : v3hit = True                           
                    elif ( (expectedXBar > 0  and expectedXBar < 6) and (v3BarQDC[expectedXBar] != DEFAULT or v3BarQDC[expectedXBar-1] != DEFAULT or v3BarQDC[expectedXBar+1] != DEFAULT) ) : v3hit = True          

                    straight = True if abs(dx) <= 1.5 and abs(dy) <= 1.5 else False
                    if straight : Denominator_straightMu.Fill(v3xExpectedPos, v3yExpectedPos)
                    else : Denominator_CR.Fill(v3xExpectedPos, v3yExpectedPos)

                    if v3hit and straight : Numerator_straightMu.Fill(v3xExpectedPos, v3yExpectedPos)
                    elif v3hit and not straight : Numerator_CR.Fill(v3xExpectedPos, v3yExpectedPos)

                    Efficiency.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)

                    if dy >= 0 : Efficiency_dyge0.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)
                    else : Efficiency_dyl0.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)

                    if dx >= 0 : Efficiency_dxge0.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)
                    else : Efficiency_dxl0.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)

                    if straight : Efficiency_straightMu.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)
                    else : Efficiency_CR.Fill(v3hit, v3xExpectedPos, v3yExpectedPos)

                    EfficiencyX.Fill(v3hit, v3xExpectedPos)
                    EfficiencyBarX.Fill(v3hit, expectedXBar)
                    EfficiencyY.Fill(v3hit, v3yExpectedPos)
                    if straight: Close_vs_farEfficiency.Fill(v3hit, int(v3yExpectedPos/7))
                    Efficiency_dx.Fill(v3hit, dx)
                    Efficiency_dy.Fill(v3hit, dy)

                    if straight: 
                        if expectedXBar == 0 : 
                            Close_vs_farEfficiency_Bar0.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar0.Fill(v3hit, v3yExpectedPos)
                        if expectedXBar == 1 : 
                            Close_vs_farEfficiency_Bar1.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar1.Fill(v3hit, v3yExpectedPos)
                        if expectedXBar == 2 : 
                            Close_vs_farEfficiency_Bar2.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar2.Fill(v3hit, v3yExpectedPos)
                        if expectedXBar == 3 : 
                            Close_vs_farEfficiency_Bar3.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar3.Fill(v3hit, v3yExpectedPos)
                        if expectedXBar == 4 : 
                            Close_vs_farEfficiency_Bar4.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar4.Fill(v3hit, v3yExpectedPos)
                        if expectedXBar == 5 : 
                            Close_vs_farEfficiency_Bar5.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar5.Fill(v3hit, v3yExpectedPos)
                        if expectedXBar == 6 : 
                            Close_vs_farEfficiency_Bar6.Fill(v3hit, int(v3yExpectedPos/6))
                            EfficiencyY_Bar6.Fill(v3hit, v3yExpectedPos)

                    # hits not compatible 
                    if not v3hit:
                        Bkg_VetoHits.Fill(v3HitBar)
                        Bkg_VetoMultiplicity.Fill(v3Multiplicity)
                        Bkg_VetoBarMultiplicity.Fill(v3BarMultiplicity)
                        if v3BarMultiplicity > 0 :
                            for i in range(7): 
                                if v3BarQDC[i] != DEFAULT : 
                                    Bkg_VetoQdc.Fill(v3BarQDC[i])
            


############################
# write histo to root file #
############################

V2LQdc.Write()
V2RQdc.Write()
Scifi1xQdc.Write()
Scifi1yQdc.Write()

V2RQDCPerBar.Write()
V2LQDCPerBar.Write()

V2_vs_V3.Write()
V2L_vs_V2R.Write()
V2_vs_scifi1x.Write()
V2_vs_scifi1y.Write()
V2_vs_scifi2x.Write()
V2_vs_scifi2y.Write()
V3_vs_scifi1x.Write()
V3_vs_scifi1y.Write()


V2LHits.Write()
V2LHitsperBar.Write()
V2RHits.Write()
V2RHitsperBar.Write()

Scifi1xQdc_residual.Write()
Scifi1xQdc_max.Write()
Scifi1xQdc_others.Write()
Scifi1yQdc_residual.Write()
Scifi1yQdc_max.Write()
Scifi1yQdc_others.Write()

Scifi1Pos.Write()
Scifi2Pos.Write()
Scifi1xPos_diff.Write()
Scifi1yPos_diff.Write()

ExpectedBarV3Residual.Write()
ExpectedPos.Write()
ExpectedPosX.Write()
ExpectedPosY.Write()

DeltaX_Distribution.Write()
DeltaY_Distribution.Write()

VetoHits.Write()
VetoHitsperBar.Write()
VetoQdc.Write()
VetoQDCPerChannel.Write()
VetoQDCPerBar.Write()

Cosmic_V2HitsperBar.Write()
Cosmic_VetoHits.Write()
Cosmic_VetoHitsperBar.Write()
Cosmic_VetoQdc.Write()
Cosmic_VetoQDCPerChannel.Write()
Cosmic_VetoQDCPerBar.Write()

Denominator_straightMu.Write()
Numerator_straightMu.Write()
Denominator_CR.Write()
Numerator_CR.Write()
Efficiency.Write()
Efficiency_dyge0.Write()
Efficiency_dyl0.Write()
Efficiency_dxge0.Write()
Efficiency_dxl0.Write()
Efficiency_straightMu.Write()
Efficiency_CR.Write()
EfficiencyX.Write()
EfficiencyBarX.Write()
EfficiencyY.Write()

Efficiency_dx.Write()
Efficiency_dy.Write()
EfficiencyY_Bar0.Write()
EfficiencyY_Bar1.Write()
EfficiencyY_Bar2.Write()
EfficiencyY_Bar3.Write()
EfficiencyY_Bar4.Write()
EfficiencyY_Bar5.Write()
EfficiencyY_Bar6.Write()
Close_vs_farEfficiency.Write()
Close_vs_farEfficiency_Bar0.Write()
Close_vs_farEfficiency_Bar1.Write()
Close_vs_farEfficiency_Bar2.Write()
Close_vs_farEfficiency_Bar3.Write()
Close_vs_farEfficiency_Bar4.Write()
Close_vs_farEfficiency_Bar5.Write()
Close_vs_farEfficiency_Bar6.Write()

Bkg_VetoHits.Write()
Bkg_VetoMultiplicity.Write()
Bkg_VetoBarMultiplicity.Write()
Bkg_VetoQdc.Write()

outfile.Close()
