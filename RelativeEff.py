import csv 
from glob import glob
from ROOT import TFile, TChain, gROOT
import ROOT


f = ROOT.TFile.Open('./results/rootfiles/output.root', 'read')
eff = f.Get('Eff_Vch')

# compute relative efficiency
first = 0
centre = 0
last = 0 
# compute mean over intervals of 10 channels
for i in range(10) :
    first += eff.GetEfficiency(15+i)
    centre += eff.GetEfficiency(25+i)
    last += eff.GetEfficiency(35+i)
first_eff = first/10
centre_eff = centre/10
last_eff = last/10

first_to_last = first_eff/last_eff
centre_to_last = centre_eff/last_eff

print(f'\nRelative eff of [15,25] wrt [35,45] is {round(first_to_last,2)}')
print(f'\nRelative eff of [25,35] wrt [35,45] is {round(centre_to_last,2)}')

# filelist = glob(f'csvfiles/textfile*')
# for file in filelist:
#     with open(file, 'r', newline='') as f:
#         csvreader = csv.reader(f)
#         map = [row for row in csvreader]
#         data.append(map[1])



# for i in range(len(filelist)):
#     average_first += data[i][0]
#     average_centre += data[i][1]
#     average_last += data[i][2]