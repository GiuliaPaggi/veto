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
#runDirectory = f"/afs/cern.ch/work/g/gpsndlhc/veto/vetoRun/run_100834/"

#DSPROPSPEED = 14.3 #cm/ns -> 1ch is 1cm 
DSPROPSPEED = 30/(4*6.25) #cm/ns -> 1ch is 1cm 

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
DSVHits = ROOT.TH1D("DSVHits", "DS Vertical Hits;  ds v channel; entries", DSn_bins, DSx_min, DSx_max) 
DSHHits = ROOT.TH1D("DSHHits", "DS Horizontal Hits; ds h channel; entries", DSn_bins, DSx_min, DSx_max)
DSVvsHHits = ROOT.TH2D("DSVvsHHits", "DS Horizontal vs Vertical Hits; ds h channel; ds v channel", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)
VetoHits = ROOT.TH1D("VetoHits", "Veto Hits; veto channel; entries", DSn_bins, DSx_min, DSx_max)
VetoHitsperBar = ROOT.TH1D("VetoHitsperBar", "Veto Hits per Bar; veto channel; entries", 7, 0, 7)
VetoHitMultiplicity = ROOT.TH1D("VetoHitMultiplicity", "Veto Hit Multiplicity;  hits per event; entries", 20, -.5, 19.5)
Cosmic_DSVHits = ROOT.TH1D("Cosmic_DSVHits", "Cosmic_DS Vertical Hits;  ds v channel; entries", DSn_bins, DSx_min, DSx_max) 
Cosmic_DSHHits = ROOT.TH1D("Cosmic_DSHHits", "Cosmic_DS Horizontal Hits; ds h channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHits = ROOT.TH1D("Cosmic_VetoHits", "Veto Hits in cosmics events;  veto channel; entries", DSn_bins, DSx_min, DSx_max)
Cosmic_VetoHitsperBar = ROOT.TH1D("Cosmic_VetoHitsperBar", "Cosmic_Veto Hits per Bar; veto channel; entries", 7, 0, 7)
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
DSLQdc = ROOT.TH1D("DSLQdc", "DSLQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
DSRQdc = ROOT.TH1D("DSRQdc", "DSRQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
DSVQdc = ROOT.TH1D("DSVQdc", "DSVQdc; qdc; entries", qdcbin, qdc_min, qdc_max)
DSQdc_RvsL = ROOT.TH2D("DSQdc_RvsL", "DSQdc_RvsL; ds R channel; ds L channel", qdcbin, qdc_min, qdc_max, qdcbin, qdc_min, qdc_max)
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
Denominatore = ROOT.TH2D("Denominatore", "Denominatore", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)

Eff_Hch = ROOT.TEfficiency( "Eff_Hch", "Efficiency per DS horizontal channel; ds h channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
Eff_Vch = ROOT.TEfficiency( "Eff_Vch", "Efficiency per DS vertical channel; ds v channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
Eff_DS  = ROOT.TEfficiency( "Eff_ch", "Efficiency per DS channel; ds v channel number; ds h channel number", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)
PositionCut_Eff_Hch = ROOT.TEfficiency( "PositionCut_Eff_Hch", "Efficiency per DS horizontal channel; ds h channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
PositionCut_Eff_Vch = ROOT.TEfficiency( "PositionCut_Eff_Vch", "Efficiency per DS vertical channel; ds v channel number; veto efficiency", DSn_bins, DSx_min, DSx_max)
PositionCut_Eff_DS  = ROOT.TEfficiency( "PositionCut_Eff_ch", "Efficiency per DS channel; ds v channel number; ds h channel number", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max)
PositionCut_Eff_GroupVch = ROOT.TEfficiency( "PositionCut_Eff_GroupVch", "Efficiency per DS vertical channel; ds v channel number; veto efficiency", 12 , 0, 12)

# Alignment
DsH_vs_Veto = ROOT.TH2D("DsH_vs_Veto", "DsH_vs_Veto; DS H ch; Veto ch", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max) 
DsV_vs_Veto = ROOT.TH2D("DsV_vs_Veto", "DsV_vs_Veto; DS V ch; Veto ch", DSn_bins, DSx_min, DSx_max, DSn_bins, DSx_min, DSx_max) 


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
    time = np.asarray(data)

    # DS boardID 1, V=[0,1], L=[2,3], R=[4,5]
    # Veto boardID 48 [6,7]

    # veto info
    vetoId = tofID[boardID == 48]
    vetoCh = tofChannel[boardID == 48]
    vetoQdc = qdc[boardID == 48]

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

                        if any(i > 30 for i in Cosmic_vetoBarQDC ) :  vetohit = True

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

                            
                            # if   (10 < DSRBar < 33  and 48 < vetoBars[i] < 57 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            # elif (15 < DSRBar < 36  and 39 < vetoBars[i] < 49 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            # elif (20 < DSRBar < 42  and 32 < vetoBars[i] < 40 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            # elif (25 < DSRBar < 50  and 24 < vetoBars[i] < 33 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            # elif (32 < DSRBar < 55  and 15 < vetoBars[i] < 25 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            # elif (38 < DSRBar < 58  and  8 < vetoBars[i] < 16 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                            # elif (45 < DSRBar < 60  and  0 < vetoBars[i] < 9  and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
            
                            # if   (10 < DSRBar < 33  and vetoBarId[i] == 7 and Cosmic_vetoBarQDC[7] > veto_cut) : PositionCut_vetohit = True
                            # elif (15 < DSRBar < 36  and vetoBarId[i] == 6 and Cosmic_vetoBarQDC[6] > veto_cut) : PositionCut_vetohit = True
                            # elif (20 < DSRBar < 42  and vetoBarId[i] == 5 and Cosmic_vetoBarQDC[5] > veto_cut) : PositionCut_vetohit = True
                            # elif (25 < DSRBar < 50  and vetoBarId[i] == 4 and Cosmic_vetoBarQDC[4] > veto_cut) : PositionCut_vetohit = True
                            # elif (32 < DSRBar < 55  and vetoBarId[i] == 3 and Cosmic_vetoBarQDC[3] > veto_cut) : PositionCut_vetohit = True
                            # elif (38 < DSRBar < 58  and vetoBarId[i] == 2 and Cosmic_vetoBarQDC[2] > veto_cut) : PositionCut_vetohit = True
                            # elif (45 < DSRBar < 60  and vetoBarId[i] == 1 and Cosmic_vetoBarQDC[1] > veto_cut) : PositionCut_vetohit = True

                            veto_cut = 30
                            if vetoMultiplicity > 5:
                                if   (10 < DSRBar < 33  and vetoBarId[i] == 6 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                                elif (15 < DSRBar < 36  and vetoBarId[i] == 5 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                                elif (20 < DSRBar < 42  and vetoBarId[i] == 4 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                                elif (25 < DSRBar < 50  and vetoBarId[i] == 3 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                                elif (32 < DSRBar < 55  and vetoBarId[i] == 2 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                                elif (38 < DSRBar < 58  and vetoBarId[i] == 1 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True
                                elif (45 < DSRBar < 60  and vetoBarId[i] == 0 and vetoQdc[i] > veto_cut) : PositionCut_vetohit = True

                    # if vetoMultiplicity > 5 :
                    #     if   (10 < DSRBar < 33  and vetoBarId[i] == 6 ) : PositionCut_vetohit = True
                    #     elif (15 < DSRBar < 36  and vetoBarId[i] == 5 ) : PositionCut_vetohit = True
                    #     elif (20 < DSRBar < 42  and vetoBarId[i] == 4 ) : PositionCut_vetohit = True
                    #     elif (25 < DSRBar < 50  and vetoBarId[i] == 3 ) : PositionCut_vetohit = True
                    #     elif (32 < DSRBar < 55  and vetoBarId[i] == 2 ) : PositionCut_vetohit = True
                    #     elif (38 < DSRBar < 58  and vetoBarId[i] == 1 ) : PositionCut_vetohit = True
                    #     elif (45 < DSRBar < 60  and vetoBarId[i] == 0 ) : PositionCut_vetohit = True
            
                    Eff_Hch.Fill(vetohit, DSLBar)
                    Eff_Vch.Fill(vetohit, DSVBar)
                    Eff_DS.Fill(vetohit, DSVBar, DSLBar)

                    PositionCut_Eff_Hch.Fill(PositionCut_vetohit, DSLBar)
                    PositionCut_Eff_Vch.Fill(PositionCut_vetohit, DSVBar)
                    PositionCut_Eff_DS.Fill(PositionCut_vetohit, DSVBar, DSLBar)
                    PositionCut_Eff_GroupVch.Fill(PositionCut_vetohit, DSVBar/5)

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

outfile.Close()
