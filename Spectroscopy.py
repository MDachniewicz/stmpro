# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 22:38:06 2023

@author: marek
"""
import numpy as np
from STMData import STMData

class Spectroscopy(STMData):
    def __init__(self, data):
        self.datatype = data.datatype
        self.parameters = data.parameter
        self.x = data.V
        self.filename = data.file
        self.xunit = 'V'
        self.unit = 'A'
        self.y_forward = None
        self.y_backward = None
        self.ramp_reversal = self.parameters['Spectroscopy.Enable_Device_1_Ramp_Reversal'][0]
        self.y_forward = data.currentForw
        self.y_forward, self.unit = self.update_unit(self.y_forward, self.unit)
        if self.ramp_reversal:
            self.ramp_reversal = True
            self.y_backward = data.currentBack
            self.y_backward, self.unit = self.update_unit(self.y_backward, 'A')

        self.x, self.xunit = self.update_unit(self.x, self.xunit)

    def get_x_range(self):
        return np.amax(self.x) - np.amin(self.x)

    def get_y_range(self):
        if self.ramp_reversal:
            max_y = max(np.amax(self.y_forward), np.amax(self.y_backward))
            min_y = min(np.amin(self.y_forward), np.amin(self.y_backward))
        else:
            max_y = np.amax(self.y_forward)
            min_y = np.amin(self.y_forward)
        return max_y-min_y
        
    def plotData(self, ax=None):
        if ax:
            if self.ramp_reversal:
                im = ax.plot(self.x, self.y_forward)
            else:
                im = ax.plot(self.x, self.y_forward, self.x, self.y_backward)


class SpectroscopyMap(Spectroscopy):
    def __init__(self, data):
        self.datatype = data.datatype
        self.parameters = data.parameter
        self.planes = data.V
        self.filename = data.file
        self.plane_unit = 'V'
        self.xunit = 'm'
        self.yunit = 'm'
        self.unit = 'A'
        self.x = data.x
        self.y = data.y
        self.z_forward = None
        self.z_backward = None
        self.ramp_reversal = self.parameters['Spectroscopy.Enable_Device_1_Ramp_Reversal'][0]
        #print(data.mtrxRef)
        self.z_forward = data.currentForw
        if self.ramp_reversal:
            self.z_backward = data.currentBack
