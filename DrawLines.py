import sys
from glob import glob
from ROOT import TFile, TChain, gROOT, TCanvas, TLegend, TLine, gPad
import ROOT

def drawLineCm(name) :
    plot = f.Get(f"{name}")
    c = ROOT.TCanvas(f"{name}", f"{name}")
    c.Range( 0, 0, 42, 42 )
    plot.Draw()
    valuescm = [6, 12, 18, 24, 30, 36]
    lines = [ROOT.TLine(x, 0, x, 42 ) for x in valuescm]

    for line in lines:    
        line.SetLineColor(ROOT.kRed)
        line.SetLineWidth(2)
        line.Draw()
        
    c.SaveAs(f"./images/{name}.png")

def drawLineCh(name) :
    plot = f.Get(f"{name}")
    c = ROOT.TCanvas(f"{name}", f"{name}")
    plot.Draw()
    c.Update()
    
    valuescm = [8, 16, 24, 32, 40, 48]
    lines = [ROOT.TLine(x+.5, gPad.GetUymin(), x+.5, gPad.GetUymax() ) for x in valuescm]

    for line in lines:    
        line.SetLineColor(ROOT.kRed)
        line.SetLineWidth(2)
        line.Draw()
        
    c.SaveAs(f"./images/{name}.png")


f = ROOT.TFile.Open(f'./results/analisysResult_allfiles.root', 'read')

drawLineCm('Efficiency')
drawLineCh('Cosmic_VetoHits')
drawLineCh('Cosmic_VetoQDCPerChannel')