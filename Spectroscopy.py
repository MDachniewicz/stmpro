# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:38:06 2023

@author: marek
"""
from STMData import STMData

class Spectroscopy(STMData):
    def __init__(self, data):
        self.data_type = data.filetype
        self.parameters = data.parameter
        self.V = data.V
        self.currentForw = data.currentForw
        self.filename = data.file
        if data.currentBack != []:
            self.rampReversal = True
            self.currentBack = data.currentBack
        else:
            self.rampReversal = False
        
    def plotData(self, ax=None):
        if ax:
            if self.rampReversal == False:
                im = ax.plot(self.V, self.currentForw)
            else:
                im = ax.plot(self.V, self.currentForw, self.V, self.currentBack)
