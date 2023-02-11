# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:38:06 2023

@author: marek
"""
from STMData import STMData

class Spectroscopy(STMData):
    def __init__(self, filetype, mtrx):
        self.data_type = mtrx.filetype
        self.parameters = mtrx.parameter
        self.V = mtrx.V
        self.currentForw = mtrx.currentForw
        if mtrx.currentBack != []:
            self.rampReversal = True
            self.currentBack = mtrx.currentBack
        else:
            self.rampReversal = False
        
    def plotData(self, ax=None):
        if ax:
            if self.rampReversal == False:
                im = ax.plot(self.V, self.currentForw)
            else:
                im = ax.plot(self.V, self.currentForw, self.V, self.currentBack)
