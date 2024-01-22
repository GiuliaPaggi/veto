import csv 
from glob import glob
from ROOT import TFile, TChain, gROOT
import ROOT


f = ROOT.TFile.Open('./results/output.root', 'read')
eff = f.Get('Eff_Vch')

# compute relative efficiency
first = 0
first_err_low = 0
first_err_up = 0

centre = 0
centre_err_low = 0
centre_err_up = 0

last = 0
last_err_low = 0
last_err_up = 0

# compute mean over intervals of 10 channels
for i in range(10) :
    first += eff.GetEfficiency(15+i)
    first_err_low += (eff.GetEfficiencyErrorLow(15+i))**2
    first_err_up += (eff.GetEfficiencyErrorUp(15+i))**2

    centre += eff.GetEfficiency(25+i)
    centre_err_low += (eff.GetEfficiencyErrorLow(25+i))**2
    centre_err_up += (eff.GetEfficiencyErrorUp(25+i))**2
    
    last += eff.GetEfficiency(35+i)
    last_err_low += (eff.GetEfficiencyErrorLow(35+i))**2
    last_err_up += (eff.GetEfficiencyErrorUp(35+i))**2
    
#compute errors 
first_err_low = (first_err_low)**.5
first_err_up = (first_err_up)**.5

centre_err_low = (centre_err_low)**.5
centre_err_up = (centre_err_up)**.5

last_err_low = (last_err_low)**.5
last_err_up = (last_err_up)**.5

first_eff = round(first/10,2)
centre_eff = round(centre/10,2)
last_eff = round(last/10,2)

first_to_last = first_eff/last_eff
centre_to_last = centre_eff/last_eff

print(f'In [15,25] the efficiency is {round(first_eff,2)} + {round(first_err_up,2)} - {round(first_err_low,2)}')
print(f'In [25,35] the efficiency is {round(centre_eff,2)} + {round(centre_err_up,2)} - {round(centre_err_low,2)}')
print(f'In [35,45] the efficiency is {round(last_eff,2)} + {round(last_err_up,2)} - {round(last_err_low,2)}')
print(f'\nRelative eff of [15,25] wrt [35,45] is {round(first_to_last,2)}')
print(f'Relative eff of [25,35] wrt [35,45] is {round(centre_to_last,2)}')




# for i in range(len(filelist)):
#     average_first += data[i][0]
#     average_centre += data[i][1]
#     average_last += data[i][2]
