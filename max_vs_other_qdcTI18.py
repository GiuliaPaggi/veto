import csv 
import sys
from glob import glob
from ROOT import TFile, TChain, gROOT, TCanvas, TLegend, gPad
import ROOT

nRun=sys.argv[1]

f = ROOT.TFile.Open(f'./results/output{nRun}.root', 'read')
V1RQDC_max = f.Get('V1RQdc_max')
V1LQDC_max = f.Get('V1LQdc_max')
V2RQDC_max = f.Get('V2RQdc_max')
V2LQDC_max = f.Get('V2LQdc_max')
V1RQDC_others = f.Get('V1RQdc_others')
V1LQDC_others = f.Get('V1LQdc_others')
V2RQDC_others = f.Get('V2RQdc_others')
V2LQDC_others = f.Get('V2LQdc_others')
V1RQDC_single = f.Get('V1RQdc_single')
V1LQDC_single = f.Get('V1LQdc_single')
V2RQDC_single = f.Get('V2RQdc_single')
V2LQDC_single = f.Get('V2LQdc_single')

# draw superimposed 7 bars
colors = [ROOT.kRed,ROOT.kGreen,ROOT.kBlue,ROOT.kMagenta,ROOT.kCyan,ROOT.kOrange,ROOT.kSpring,ROOT.kTeal,ROOT.kViolet,ROOT.kYellow]


V1RQDC_max.SetLineColor(colors[0])
V1RQDC_others.SetLineColor(colors[2])
V1RQDC_single.SetLineColor(colors[5])

V1LQDC_max.SetLineColor(colors[0])
V1LQDC_others.SetLineColor(colors[2])
V1LQDC_single.SetLineColor(colors[5])

V2RQDC_max.SetLineColor(colors[0])
V2RQDC_others.SetLineColor(colors[2])
V2RQDC_single.SetLineColor(colors[5])

V2LQDC_max.SetLineColor(colors[0])
V2LQDC_others.SetLineColor(colors[2])
V2LQDC_single.SetLineColor(colors[5])


c = ROOT.TCanvas("c", "c")
V1RQDC_single.Draw()
V1RQDC_others.Draw("same")
V1RQDC_max.Draw("same")
c.SaveAs("./images/V1Rqdc.png")

c1 = ROOT.TCanvas("c1", "c1")
c1.cd()
V1LQDC_single.Draw()
V1LQDC_others.Draw("same")
V1LQDC_max.Draw("same")
c1.SaveAs("./images/V1Lqdc.png")

c2 = ROOT.TCanvas("c2", "c2")
c2.cd()
V2LQDC_single.Draw()
V2LQDC_others.Draw("same")
V2LQDC_max.Draw("same")
c2.SaveAs("./images/V2Lqdc.png")

c3 = ROOT.TCanvas("c3", "c3")
c3.cd()
V2RQDC_single.Draw()
V2RQDC_others.Draw("same")
V2RQDC_max.Draw("same")
c3.SaveAs("./images/V2Rqdc.png")