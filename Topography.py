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
        self.filename=mtrx.file
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
            
    def XYZ(self):
        return np.hstack([self.X.reshape(-1,1), self.Y.reshape(-1,1), self.Z.reshape(-1,1)])
    
    def saveXYZ(self, filename = None):
        if filename == None:
            filename=self.filename+'.XYZ'
        XYZ=self.XYZ()
        np.savetxt(filename, XYZ)
        
            
    def level_linewise(self):
        for i in range(self.Z.shape[0]):
            a,b=np.linalg.lstsq(np.vstack([self.X[i,:], np.ones(len(self.X[i,:]))]).T,self.Z[i,:],rcond=None)[0]
            self.Z[i,:]=self.Z[i,:]-self.X[i,:]*a-b
            
            