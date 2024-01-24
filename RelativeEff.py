import csv 
import sys
from glob import glob
from ROOT import TFile, TChain, gROOT
import ROOT

nRun=sys.argv[1]

f = ROOT.TFile.Open(f'./results/output{nRun}.root', 'read')
eff = f.Get('PositionCut_Eff_Vch')

roundDigits = 5
nBins = 10

# compute relative efficiency
first = 0
first_err_low = 0
first_err_up = 0
first_bin=20

centre = 0
centre_err_low = 0
centre_err_up = 0
centre_bin=30

last = 0
last_err_low = 0
last_err_up = 0
last_bin=40

# compute mean over intervals of 10 channels
for i in range(nBins) :
    first += eff.GetEfficiency(first_bin+i)
    first_err_low += (eff.GetEfficiencyErrorLow(first_bin+i))**2
    first_err_up += (eff.GetEfficiencyErrorUp(first_bin+i))**2

    centre += eff.GetEfficiency(centre_bin+i)
    centre_err_low += (eff.GetEfficiencyErrorLow(centre_bin+i))**2
    centre_err_up += (eff.GetEfficiencyErrorUp(centre_bin+i))**2
    
    last += eff.GetEfficiency(last_bin+i)
    last_err_low += (eff.GetEfficiencyErrorLow(last_bin+i))**2
    last_err_up += (eff.GetEfficiencyErrorUp(last_bin+i))**2
    
#compute errors 
first_err_low = (first_err_low)**.5
first_err_up = (first_err_up)**.5

centre_err_low = (centre_err_low)**.5
centre_err_up = (centre_err_up)**.5

last_err_low = (last_err_low)**.5
last_err_up = (last_err_up)**.5

first_eff = round(first/nBins,roundDigits)
centre_eff = round(centre/nBins,roundDigits)
last_eff = round(last/nBins,roundDigits)

first_to_last = first_eff/last_eff
centre_to_last = centre_eff/last_eff

print(f'In [{first_bin},{first_bin+nBins}] the efficiency is {round(first_eff,roundDigits)} + {round(first_err_up,roundDigits)} - {round(first_err_low,roundDigits)}')
print(f'In [{centre_bin},{centre_bin+nBins}] the efficiency is {round(centre_eff,roundDigits)} + {round(centre_err_up,roundDigits)} - {round(centre_err_low,roundDigits)}')
print(f'In [{last_bin},{last_bin+nBins}] the efficiency is {round(last_eff,roundDigits)} + {round(last_err_up,roundDigits)} - {round(last_err_low,roundDigits)}')
print(f'\nRelative eff of [{first_bin},{first_bin+nBins}] wrt [{last_bin},{last_bin+nBins}] is {round(first_to_last,roundDigits)}')
print(f'Relative eff of [{centre_bin},{centre_bin+nBins}] wrt [{last_bin},{last_bin+nBins}] is {round(centre_to_last,roundDigits)}')

with open(f'./results/RelEff_run{nRun}.txt', 'w') as f:
    f.write(f'In [15,25] the efficiency is {round(first_eff,roundDigits)} + {round(first_err_up,roundDigits)} - {round(first_err_low,roundDigits)}')
    f.write(f'\nIn [25,35] the efficiency is {round(centre_eff,roundDigits)} + {round(centre_err_up,roundDigits)} - {round(centre_err_low,roundDigits)}')
    f.write(f'\nIn [35,45] the efficiency is {round(last_eff,roundDigits)} + {round(last_err_up,roundDigits)} - {round(last_err_low,roundDigits)}')
    f.write(f'\n\nRelative eff of [15,25] wrt [35,45] is {round(first_to_last,roundDigits)}')
    f.write(f'\nRelative eff of [25,35] wrt [35,45] is {round(centre_to_last,roundDigits)}')
