import csv 
import sys
from glob import glob
from ROOT import TFile, TChain, gROOT, TCanvas, TLegend, gPad
import ROOT

nRun=sys.argv[1]

f = ROOT.TFile.Open(f'./results/output{nRun}.root', 'read')
RQDC_max = f.Get('V1RQdc_max')
LQDC_max = f.Get('V1RQdc_max')
VQDC_max = f.Get('V1RQdc_max')
RQDC_others = f.Get('DSRQdc_others')
LQDC_others = f.Get('DSLQdc_others')
VQDC_others = f.Get('DSVQdc_others')
RQDC_single = f.Get('DSRQdc_single')
LQDC_single = f.Get('DSLQdc_single')
VQDC_single = f.Get('DSVQdc_single')
# draw superimposed 7 bars
colors = [ROOT.kRed,ROOT.kGreen,ROOT.kBlue,ROOT.kMagenta,ROOT.kCyan,ROOT.kOrange,ROOT.kSpring,ROOT.kTeal,ROOT.kViolet,ROOT.kYellow]


RQDC_max.SetLineColor(colors[0])
RQDC_others.SetLineColor(colors[2])
RQDC_single.SetLineColor(colors[5])
LQDC_max.SetLineColor(colors[0])
LQDC_others.SetLineColor(colors[2])
RQDC_single.SetLineColor(colors[5])
VQDC_max.SetLineColor(colors[0])
VQDC_others.SetLineColor(colors[2])
RQDC_single.SetLineColor(colors[5])

c = ROOT.TCanvas("c", "c")
RQDC_others.Draw()
RQDC_max.Draw("same")
RQDC_single.Draw("same")
c.SaveAs("./images/Rqdc.png")

c1 = ROOT.TCanvas("c1", "c1")
c1.cd()
LQDC_others.Draw()
LQDC_max.Draw("same")
LQDC_single.Draw("same")
c1.SaveAs("./images/Lqdc.png")

c2 = ROOT.TCanvas(f"Relative Eff", f"Relative Eff")
c2.cd()
VQDC_others.Draw()
VQDC_max.Draw("same")
VQDC_single.Draw("same")
c2.SaveAs("./images/Vqdc.png")