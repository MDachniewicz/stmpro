# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 20:58:54 2023

@author: marek
"""
import numpy as np
from STMData import STMData

import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

class Topography(STMData):
    
    def __init__(self, mtrx, ax=0):
        self.data_type='Z'
        self.parameters=mtrx.parameter
        self.X=mtrx.x
        self.Y=mtrx.y
        if ax==0:
            self.Z=mtrx.imageForwUp
            self.name='Topography Image Forward-Up ' + mtrx.file
        elif ax==1:
            self.Z=mtrx.imageBackUp
        elif ax==2:
            self.Z=mtrx.imageForwDown
        elif ax==3:
            self.Z=mtrx.imageBackDown
            
    def plotData(self, ax=None):
        if ax:
            im = ax.pcolor(self.X*10**9, self.Y*10**9, self.Z)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            ax.axis('equal')
            plt.colorbar(im, cax=cax)
            