import csv 
import sys
from glob import glob
from ROOT import TFile, TChain, gROOT, TCanvas, TLegend, gPad
import ROOT

nRun=sys.argv[1]

f = ROOT.TFile.Open(f'./results/output{nRun}.root', 'read')
eff = f.Get('PositionCut_Eff_GroupVch')
barEff = [None]*7
relBarEff = [0]*7
for i in range(7):
    barEff[i]= f.Get(f'PositionCut_Bar{i}Eff_GroupVch')

# compute relative efficiency

relEff = eff.GetEfficiency(1)/eff.GetEfficiency(3)

for i in range(7):
    relBarEff[i] = barEff[i].GetEfficiency(1)/barEff[i].GetEfficiency(3)

with open(f'./results/RelEff_run{nRun}.txt', 'w') as f:
    f.write(f'Veto relative efficiency is {relEff}')
    for i in range(7) :
        f.write(f'\nVeto bar {i} relative efficiency is {relBarEff[i]}')

# draw superimposed 7 bars
colors = [ROOT.kRed,ROOT.kGreen,ROOT.kBlue,ROOT.kMagenta,ROOT.kCyan,ROOT.kOrange,ROOT.kSpring,ROOT.kTeal,ROOT.kViolet,ROOT.kYellow]
c = ROOT.TCanvas(f"Relative Eff Bars", f"Relative Eff Bars")
l = ROOT.TLegend(0.1, 0.7, 0.3, 0.9)

for i in range(7):
    barEff[i].SetLineColor(colors[i])
    l.AddEntry(barEff[i], f"Bar {i}")


barEff[0].Draw()
gPad.Update()
graph = barEff[0].GetPaintedGraph()
graph.SetMinimum(0)
graph.SetMaximum(1) 
gPad.Update()
for i in range(1, 7):
    barEff[i].Draw("same")
l.Draw("same")
c.SaveAs("relEff.png")

c2 = ROOT.TCanvas(f"Relative Eff", f"Relative Eff")
c2.cd()
eff.Draw()
gPad.Update()
graph = eff.GetPaintedGraph()
graph.SetMinimum(0)
graph.SetMaximum(1) 
gPad.Update()
c2.SaveAs("allbar.png")