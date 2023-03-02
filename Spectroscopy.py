# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:38:06 2023

@author: marek
"""
import numpy as np
from STMData import STMData

class Spectroscopy(STMData):
    def __init__(self, data):
        self.data_type = data.filetype
        self.parameters = data.parameter
        self.V = data.V
        self.current_forward = data.currentForw
        self.filename = data.file
        self.xunit = 'V'
        self.unit = 'A'
        if data.currentBack != []:
            self.rampReversal = True
            self.current_backward = data.currentBack
        else:
            self.rampReversal = False

        self.current_forward, self.unit = self.update_unit(self.current_forward, self.unit)
        self.V, self.xunit = self.update_unit(self.V, self.xunit)

    def get_x_range(self):
        range = np.amax(self.V) - np.amin(self.V)
        return range

    def get_z_range(self):
        max_z = max(np.amax(self.current_forward), np.amax(self.current_backward))
        min_z = min(np.amin(self.current_forward), np.amin(self.current_backward))
        range = max_z-min_z
        return range
        
    def plotData(self, ax=None):
        if ax:
            if self.rampReversal == False:
                im = ax.plot(self.V, self.current_forward)
            else:
                im = ax.plot(self.V, self.current_forward, self.V, self.currentBack)
