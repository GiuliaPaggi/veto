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
    return -1

def return_bar(map, tofpet_id, tofpet_channel):    
    for row in map:
        if (row[4] == str(tofpet_channel) and row[3] == str(tofpet_id%2)):
            return int(np.floor((int(row[0])-1)/8))
    return -1

#############
# read data #
#############

runN = sys.argv[1]
#runDirectory = f"/eos/experiment/sndlhc/raw_data/commissioning/veto/run_{runN}/"
runDirectory = f"/eos/experiment/sndlhc/raw_data/commissioning/TI18/data/run_00{runN}/"


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

DSn_bins = 59
DSx_min = -.5
DSx_max = 57.5

# Hits info 

VetoHits = ROOT.TH1D("VetoHits", "Veto Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
VetoHitsperBar = ROOT.TH1D("VetoHitsperBar", "Veto Hits per Bar; veto bar; entries", 7, 0, 7)
VetoHitMultiplicity = ROOT.TH1D("VetoHitMultiplicity", "Veto Hit Multiplicity;  hits per event; entries", 20, -.5, 19.5)
Cosmic_V1Hits = ROOT.TH1D("Cosmic_V1Hits", "Cosmic Veto 1 Hits;  channel; entries", DSn_bins, DSx_min, DSx_max) 
Cosmic_V2Hits = ROOT.TH1D("Cosmic_V2Hits", "Cosmic Veto 2 Hits; channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_V1HitsperBar = ROOT.TH1D("Cosmic_V1HitsperBar", "Cosmic Veto 1 Hits perBar;  bar; entries", 7, 0, 7) 
Cosmic_V2HitsperBar = ROOT.TH1D("Cosmic_V2HitsperBar", "Cosmic Veto 2 Hits perBar; bar; entries", 7, 0, 7)
Cosmic_VetoHits = ROOT.TH1D("Cosmic_VetoHits", "Veto Hits in cosmics events;  veto channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitsperBar = ROOT.TH1D("Cosmic_VetoHitsperBar", "Cosmic_Veto Hits per Bar; veto channel; entries", 9, -.5, 5.5)
Cosmic_VetoHitsperPosition = ROOT.TH1D("Cosmic_VetoHitsperPosition", "Cosmic_VetoHitsperPosition; ds V channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitMultiplicity = ROOT.TH1D("Cosmic_VetoHitMultiplicity", "Veto Hit Multiplicity in cosmic ray events;  hits per event; entries", 20, -.5, 19.5)
Bkg_VetoHits = ROOT.TH1D("Bkg_VetoHits", "Veto Hits in not cosmics events; veto channel; entries", DSn_bins, DSx_min, DSx_max)
Bkg_VetoMultiplicity = ROOT.TH1D("Bkg_VetoMultiplicity", "Veto Hit Multiplicity in not cosmics; hits per event; entries", 20, -.5, 19.5)
Noise_VetoHits = ROOT.TH1D("Noise_VetoHits", "Veto Hits w/o ds hits;  veto channel; entries", DSn_bins, DSx_min, DSx_max)
Noise_VetoMultiplicity = ROOT.TH1D("Noise_VetoMultiplicity", "Veto Hit Multiplicity w/o ds hits;  hits per event; entries", 20, -.5, 19.5)
Simp_perBar = ROOT.TH2D("Simp_perBar", "Simp_perBar", 7, 0, 7, 9, 0, 9)
 
# qdc
qdcbin = 200
qdc_min = 1
qdc_max = 201

V1LQdc = ROOT.TH1D("V1LQdc", "V1LQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V1RQdc = ROOT.TH1D("V1RQdc", "V1RQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V1Qdc_RvsL = ROOT.TH2D("V1Qdc_RvsL", "V1Qdc_RvsL; V1 R channel; V1 L channel", qdcbin, qdc_min, qdc_max, qdcbin, qdc_min, qdc_max)
V1QdcDiff = ROOT.TH1D("V1QdcDiff", "V1Qdc Difference; R-L QDC; Entries", 200, -100, 100)

V2LQdc = ROOT.TH1D("V2LQdc", "V2LQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V2RQdc = ROOT.TH1D("V2RQdc", "V2RQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
V2Qdc_RvsL = ROOT.TH2D("V2Qdc_RvsL", "V2Qdc_RvsL; V2 R channel; V2 L channel", qdcbin, qdc_min, qdc_max, qdcbin, qdc_min, qdc_max)
V2QdcDiff = ROOT.TH1D("V2QdcDiff", "V2Qdc Difference; R-L QDC; Entries", 200, -100, 100)

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

PositionCut_Eff_GroupVch = ROOT.TEfficiency( "PositionCut_Eff_GroupVch", "Efficiency per DS vertical channel; ds v channel number; veto efficiency", 3 , 0, 3)
PositionCut_Bar0Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar0Eff_GroupVch", "PositionCut_Bar0Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar1Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar1Eff_GroupVch", "PositionCut_Bar1Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar2Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar2Eff_GroupVch", "PositionCut_Bar2Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar3Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar3Eff_GroupVch", "PositionCut_Bar3Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar4Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar4Eff_GroupVch", "PositionCut_Bar4Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar5Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar5Eff_GroupVch", "PositionCut_Bar5Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar6Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar6Eff_GroupVch", "PositionCut_Bar6Eff_GroupVch", 3, 0, 3 )
PositionCut_Bar7Eff_GroupVch = ROOT.TEfficiency ( "PositionCut_Bar7Eff_GroupVch", "PositionCut_Bar7Eff_GroupVch", 3, 0, 3 )

#Alignment

V1_vs_V2 = ROOT.TH2D("V1_vs_V2", "V1_vs_V2; v1 bar; v2 bar", 7, 0, 7, 7, 0, 7)
Ch_V1_vs_V2 = ROOT.TH2D("Ch_V1_vs_V2", "Ch_V1_vs_V2; v1 channel; v2 channel", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)

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
    vetoId = tofID[boardID == 58]
    vetoCh = tofChannel[boardID == 58]
    vetoQdc = qdc[boardID == 58]

    v1LId = vetoId[(vetoId<2)]
    v1RId = vetoId[(vetoId>5)]
    v2LId = vetoId[(vetoId>1) & (vetoId<4)]
    v2RId = vetoId[(vetoId>3) & (vetoId<6)]

    if len(v1LId) > 1 and len(v1RId) > 1 and len(v2LId) > 1 and len(v2RId) > 1 :       
        
        v1LPin = vetoCh[(vetoId<2)]
        v1RPin = vetoCh[(vetoId>5)]
        v2LPin = vetoCh[(vetoId>1) & (vetoId<4)]
        v2RPin = vetoCh[(vetoId>3) & (vetoId<6)]
        
        # v1LBar = [return_bar(mapVeto, v1LId[i], v1LCh[i]) for i in range(len(v1LId))]
        # v1RBar = [return_bar(mapVeto, v1RId[i], v1RCh[i]) for i in range(len(v1RId))]
        # v2LBar = [return_bar(mapVeto, v2LId[i], v2LCh[i]) for i in range(len(v2LId))]
        # v2RBar = [return_bar(mapVeto, v2RId[i], v2RCh[i]) for i in range(len(v2RId))]

        v1LQdc = vetoQdc[(vetoId<2)]
        v1RQdc = vetoQdc[(vetoId>5)]
        v2LQdc = vetoQdc[(vetoId>1) & (vetoId<4)]
        v2RQdc = vetoQdc[(vetoId>3) & (vetoId<6)]

        v1LHitPin = v1LPin[np.array(v1LQdc).argmax()]
        v1RHitPin = v1RPin[np.array(v1RQdc).argmax()]
        v2LHitPin = v2LPin[np.array(v2LQdc).argmax()]
        v2RHitPin = v2RPin[np.array(v2RQdc).argmax()]
        
        v1LHitID = v1LId[np.array(v1LQdc).argmax()]
        v1RHitID = v1RId[np.array(v1RQdc).argmax()]
        v2LHitID = v2LId[np.array(v2LQdc).argmax()]
        v2RHitID = v2RId[np.array(v2RQdc).argmax()]

        v1LCh = return_ch(mapVeto, v1LHitID, v1LHitPin) 
        v1RCh = return_ch(mapVeto, v1RHitID, v1RHitPin)
        v2LCh = return_ch(mapVeto, v2LHitID, v2LHitPin)
        v2RCh = return_ch(mapVeto, v2RHitID, v2RHitPin)

        v1LBar = return_bar(mapVeto, v1LHitID, v1LHitPin) 
        v1RBar = return_bar(mapVeto, v1RHitID, v1RHitPin)
        v2LBar = return_bar(mapVeto, v2LHitID, v2LHitPin)
        v2RBar = return_bar(mapVeto, v2RHitID, v2RHitPin)

        if v1LBar == v1RBar and v2LBar == v2RBar:

            v1LhitQdc = np.max(v1LQdc)
            v1RhitQdc = np.max(v1RQdc)
            v2LhitQdc = np.max(v2LQdc)
            v2RhitQdc = np.max(v2RQdc)

            V1LQdc.Fill(v1LhitQdc)
            V1RQdc.Fill(v1RhitQdc)
            V2LQdc.Fill(v2LhitQdc)
            V2RQdc.Fill(v2RhitQdc)

            V1QdcDiff.Fill( v1RhitQdc - v1LhitQdc)
            V2QdcDiff.Fill( v2RhitQdc - v2LhitQdc)

            V1_vs_V2.Fill(v1LBar, v2LBar)
            Ch_V1_vs_V2.Fill(v1LCh, v2LCh)
"""
    vetoMultiplicity = len(vetoId)
    
    if vetoMultiplicity > 0:        
        
        VetoHitMultiplicity.Fill(vetoMultiplicity)
        
        vetoBars = [return_bar(mapVeto, vetoId[i], vetoCh[i]) for i in range(vetoMultiplicity)]
        vetoBarId = [int(np.floor((i-1)/8)) for i in vetoBars]

        vetoBarQDC = np.zeros(8)

        for i in range(vetoMultiplicity):
            
            VetoHits.Fill(vetoBars[i])
            VetoHitsperBar.Fill(vetoBarId[i])
            vetoBarQDC[vetoBarId[i]] += vetoQdc[i]
            VetoQdc.Fill(vetoQdc[i])
            VetoQDCPerChannel.Fill(vetoBars[i], vetoQdc[i])
        
        for i in vetoBarId : VetoQDCPerBar.Fill(i, vetoBarQDC[i])

    # DS info
    DStofID = tofID[boardID == 1]
    DsMultiplicity = len(DStofID)

    DStofCh = tofChannel[boardID == 1]
    DSQdc = qdc[boardID == 1]

    #############################
    # select cosmic rays events #
    #############################

    if DsMultiplicity > 0:

        DSRID = DStofID[DStofID>3]
        DSLID = DStofID[(DStofID>1) & (DStofID<4)]
        DSVID = DStofID[DStofID<2]

        #########################
        # select cosmics events #
        #########################

        #ask for 3 hit in total in ds-> 1 ds R 1 ds L and 1 ds V     

        if len(DSLID) > 0 and len(DSRID) > 0 and len(DSVID) > 0:

            DSLCh = DStofCh[(DStofID>1) & (DStofID<4)]
            DSRCh = DStofCh[DStofID>3]
            DSVCh = DStofCh[DStofID<2]

            LQdc = DSQdc[(DStofID>1) & (DStofID<4)]
            RQdc = DSQdc[DStofID>3]
            VQdc = DSQdc[DStofID<2]
            
            Rqdc = np.max(RQdc)
            Lqdc = np.max(LQdc)
            Vqdc = np.max(VQdc)

            #select hits with the highest qdc value (signal should be > noise)

            if Rqdc > 0 and Lqdc > 0 and Vqdc > 0:

                DSRHitCh = DSRCh[np.array(RQdc).argmax()]
                DSLHitCh = DSLCh[np.array(LQdc).argmax()]
                DSVHitCh = DSVCh[np.array(VQdc).argmax()]
                
                DSRHitID = DSRID[np.array(RQdc).argmax()]
                DSLHitID = DSLID[np.array(LQdc).argmax()]
                DSVHitID = DSVID[np.array(VQdc).argmax()]
                            
                DSRBar = return_bar(mapDS, DSRHitID, DSRHitCh)
                DSLBar = return_bar(mapDS, DSLHitID, DSLHitCh)
                DSVBar = return_bar(mapDS, DSVHitID, DSVHitCh)  

                DSVHits.Fill(DSVBar)
                
                if DSRBar == DSLBar: 
                    DSVvsHHits.Fill(DSLBar, DSVBar)
                    DSHHits.Fill(DSLBar)

                    DSLQdc.Fill(Lqdc)
                    DSRQdc.Fill(Rqdc)
                    DSVQdc.Fill(Vqdc)
                    DSQdc_RvsL.Fill(Rqdc, Lqdc)
                
                # cut on qdc to ensure is a MIP signal 

                if ( Lqdc > 35 ) and ( Rqdc > 30 ) and ( Vqdc > 15 )  and DSRBar == DSLBar:     

                    Denominatore.Fill(DSVBar, DSLBar)

                    Cosmic_DSVHits.Fill(DSVBar)
                    Cosmic_DSHHits.Fill(DSRBar)
                    
                    Cosmic_vetoBarQDC = np.zeros(8)
                    
                    for i in range(vetoMultiplicity) : Cosmic_vetoBarQDC[vetoBarId[i]] += vetoQdc[i]

                    for i in vetoBarId : 
                        Simp_perBar.Fill(i, len(vetoBarId))
                    
                    vetohit = False
                    PositionCut_vetohit = False

                    if vetoMultiplicity > 0: 

                        #if any(i > 30 for i in Cosmic_vetoBarQDC ) :  vetohit = True
                        vetohit = True

                        Cosmic_VetoHitMultiplicity.Fill(vetoMultiplicity)

                        for i in range(vetoMultiplicity) : 
                            
                            Cosmic_VetoQDCPerBar.Fill(vetoBarId[i], Cosmic_vetoBarQDC[vetoBarId[i]])
                            Cosmic_VetoHits.Fill(vetoBars[i])
                            Cosmic_VetoHitsperBar.Fill(vetoBarId[i])
                            Cosmic_VetoHitsperPosition.Fill(DSVBar)
                            
                            Cosmic_VetoQdc.Fill(vetoQdc[i])
                            Cosmic_VetoQDCPerChannel.Fill(vetoBars[i], vetoQdc[i])
                            VetoQDCPerPosition.Fill(DSVBar, vetoQdc[i])

                            DsH_vs_Veto.Fill(DSLBar, vetoBars[i])
                            DsV_vs_Veto.Fill(DSVBar, vetoBars[i])

                            veto_cut = 30
                            if   (10 < DSRBar < 33  and vetoBarId[i] == 6 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            elif (15 < DSRBar < 36  and vetoBarId[i] == 5 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            elif (20 < DSRBar < 42  and vetoBarId[i] == 4 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            elif (25 < DSRBar < 50  and vetoBarId[i] == 3 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            elif (32 < DSRBar < 55  and vetoBarId[i] == 2 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            elif (38 < DSRBar < 58  and vetoBarId[i] == 1 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            elif (45 < DSRBar < 60  and vetoBarId[i] == 0 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
        
                    Eff_Hch.Fill(vetohit, DSLBar)
                    Eff_Vch.Fill(vetohit, DSVBar)
                    Eff_DS.Fill(vetohit, DSVBar, DSLBar)

                    PositionCut_Eff_Hch.Fill(PositionCut_vetohit, DSLBar)
                    PositionCut_Eff_Vch.Fill(PositionCut_vetohit, DSVBar)
                    PositionCut_Eff_DS.Fill(PositionCut_vetohit, DSVBar, DSLBar)
                    

                    #fill eff plots
                    if 21 < DSVBar < 59:
                        bin = int((DSVBar-23)/12)
                        for i in range(vetoMultiplicity) :
                            PositionCut_Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 0 : PositionCut_Bar0Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 1 : PositionCut_Bar1Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 2 : PositionCut_Bar2Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 3 : PositionCut_Bar3Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 4 : PositionCut_Bar4Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 5 : PositionCut_Bar5Eff_GroupVch.Fill(PositionCut_vetohit, bin)
                            if vetoBarId[i] == 6 : PositionCut_Bar6Eff_GroupVch.Fill(PositionCut_vetohit, bin)



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
DSVvsHHits.Write()
VetoHits.Write()
VetoHitsperBar.Write()
VetoHitMultiplicity.Write()
Bkg_VetoHits.Write()
Bkg_VetoMultiplicity.Write()
Noise_VetoHits.Write()
Noise_VetoMultiplicity.Write()
Simp_perBar.Write()

#efficiencies histo
Denominatore.Write()
Eff_Hch.Write()
Eff_Vch.Write()
Eff_DS.Write()

PositionCut_Eff_Hch.Write()
PositionCut_Eff_Vch.Write()
PositionCut_Eff_DS.Write()
PositionCut_Eff_GroupVch.Write()
PositionCut_Bar0Eff_GroupVch.Write()
PositionCut_Bar1Eff_GroupVch.Write()
PositionCut_Bar2Eff_GroupVch.Write()
PositionCut_Bar3Eff_GroupVch.Write()
PositionCut_Bar4Eff_GroupVch.Write()
PositionCut_Bar5Eff_GroupVch.Write()
PositionCut_Bar6Eff_GroupVch.Write()

#ds qdc distribution
DSLQdc.Write()
DSRQdc.Write()
DSVQdc.Write()
DSQdc_RvsL.Write()

#veto qdc distribution
VetoQDCPerPosition.Write()
VetoQDCPerChannel.Write()
VetoQDCPerBar.Write()
VetoQdc.Write()

Cosmic_DSVHits.Write() 
Cosmic_DSHHits.Write()
Cosmic_VetoHits.Write()
Cosmic_VetoHitsperBar.Write()
Cosmic_VetoQDCPerChannel.Write()
Cosmic_VetoHitsperPosition.Write()
Cosmic_VetoHitMultiplicity.Write()
Cosmic_VetoQdc.Write()
Cosmic_VetoQDCPerBar.Write()
Bkg_VetoQdc.Write()
Noise_VetoQdc.Write()

# relative alignment
DsH_vs_Veto.Write()
DsV_vs_Veto.Write()


"""

V1LQdc.Write()
V1RQdc.Write()
V2LQdc.Write()
V2RQdc.Write()

V1QdcDiff.Write()
V2QdcDiff.Write()

V1_vs_V2.Write()
Ch_V1_vs_V2.Write()

outfile.Close()