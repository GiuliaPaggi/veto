import sys
from glob import glob
from ROOT import TFile, TChain, gROOT, TCanvas, TLegend, gPad, gStyle
import ROOT

CANVASDIM = 1000
gStyle.SetOptStat("ne")

f = ROOT.TFile.Open(f'./results/blg29/output8.root', 'read')
eff = f.Get('PositionCut_Eff_GroupVch')
errors = [0]*3
barErrors = ([0,0,0])*7
barEff = [None]*7
relBarEff = [0]*7
relBarError = [0]*7

for i in range(7):
    barEff[i]= f.Get(f'PositionCut_Bar{i}Eff_GroupVch')

# compute relative efficiency

relEff = eff.GetEfficiency(1)/eff.GetEfficiency(3)

for i in range(1, 4, 2) : 
    low = eff.GetEfficiencyErrorLow(i)
    up = eff.GetEfficiencyErrorUp(i)
    errors[i-1] = low if (low > up) else up

# in division propagation of error -> relative error is sum of relatives error
eff_error = ((errors[0]/eff.GetEfficiency(1)) + (errors[2]/eff.GetEfficiency(3))) * relEff
#eff.GetPassedHistogram().GetBinContent(1)

for i in range(7):
    relBarEff[i] = barEff[i].GetEfficiency(1)/barEff[i].GetEfficiency(3)

    for j in range(1, 4, 2) : 
        low = eff.GetEfficiencyErrorLow(j)
        up = eff.GetEfficiencyErrorUp(j)
        barErrors[3*i+(j-1)] = low if (low > up) else up
    
    relBarError[i] = ( ( barErrors[3*i] / barEff[i].GetEfficiency(1) ) + ( barErrors[(3*i)+2] / barEff[i].GetEfficiency(3) ) ) * relBarEff[i]


with open(f'./results/blg29/RelEff.txt', 'w') as f:
    f.write(f'Veto relative efficiency is {round(relEff,4)} pm {round(eff_error,4)}')
    for i in range(7) :
        f.write(f'\nVeto bar {i} relative efficiency is {round(relBarEff[i],4)} pm {round(relBarError[i], 4)}')

# draw superimposed 7 bars
colors = [ROOT.kRed,ROOT.kGreen,ROOT.kBlue,ROOT.kMagenta,ROOT.kCyan,ROOT.kOrange,ROOT.kOrange+3,ROOT.kTeal,ROOT.kSpring,ROOT.kViolet,ROOT.kYellow]
c = ROOT.TCanvas(f"Relative Eff Bars", f"Relative Eff Bars", CANVASDIM+500, CANVASDIM, CANVASDIM+500, CANVASDIM)
l = ROOT.TLegend(0.1, 0.1, 0.3, 0.4)

l.AddEntry(eff, "all")
for i in range(7):
    barEff[i].SetLineColor(colors[i])
    l.AddEntry(barEff[i], f"Bar {i}")


eff.Draw()
gPad.Update()
graph = eff.GetPaintedGraph()
graph.SetMinimum(0)
graph.SetMaximum(1) 
gPad.Update()
for i in range(0, 7):
    barEff[i].Draw("same")
l.Draw("same")
c.SaveAs("./images/relEff.png")

c2 = ROOT.TCanvas(f"Relative Eff", f"Relative Eff", CANVASDIM+500, CANVASDIM, CANVASDIM+500, CANVASDIM)
c2.cd()
eff.Draw()
gPad.Update()
graph = eff.GetPaintedGraph()
graph.SetMinimum(0)
graph.SetMaximum(1) 
gPad.Update()
c2.SaveAs("./images/allbar.png")