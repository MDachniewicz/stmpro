# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 20:58:54 2023

@author: marek
"""
import numpy as np
from STMData import STMData
import Filters
import Curves
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


class Topography(STMData):

    def __init__(self, filetype, data, ax=0):
        if filetype == 'mtrx':
            self.__initMtrx(data, ax)
        if filetype == 'xyz':
            self.__initXYZ(data)
        self.xrange = (self.X.max()-self.X.min())*10**9
        self.yrange = (self.Y.max()-self.Y.min())*10**9
        self.set_zero_level()

    def __initMtrx(self, mtrx, ax):
        self.filetype = mtrx.filetype
        self.parameters = mtrx.parameter
        self.X = mtrx.x
        self.Y = mtrx.y
        self.filename = mtrx.file
        self.xunit = 'nm'
        if self.filetype == 'Z':
            self.__initMtrxZ(mtrx, ax)
        if self.filetype == 'I':
            self.__initMtrxZ(mtrx, ax)

    def __initMtrxZ(self, mtrx, ax=0):
        self.unit = 'nm'
        if ax == 0:
            self.Z = mtrx.imageForwUp
            self.name = 'Topography Image Forward-Up ' + mtrx.file
        elif ax == 1:
            self.Z = mtrx.imageBackUp
        elif ax == 2:
            self.Z = mtrx.imageForwDown
        elif ax == 3:
            self.Z = mtrx.imageBackDown

    def __initMtrxI(self, mtrx, ax=0):
        self.unit = 'A'
        if ax == 0:
            self.Z = mtrx.imageForwUp
            self.name = 'Topography Image Forward-Up ' + mtrx.file
        elif ax == 1:
            self.Z = mtrx.imageBackUp
        elif ax == 2:
            self.Z = mtrx.imageForwDown
        elif ax == 3:
            self.Z = mtrx.imageBackDown

    def __initXYZ(self, data):
        self.X = data[0]
        self.Y = data[1]
        self.Z = data[2]
        self.filename = data[3]


    def plotData(self, ax=None):
        if ax:
            im = ax.pcolor(self.X * 10 ** 9, self.Y * 10 ** 9, self.Z)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            ax.axis('equal')
            plt.colorbar(im, cax=cax)

    def XYZ(self):
        return np.hstack([self.X.reshape(-1, 1), self.Y.reshape(-1, 1), self.Z.reshape(-1, 1)])

    def saveXYZ(self, filename=None):
        if filename == None:
            filename = self.filename + '.XYZ'
        XYZ = self.XYZ()
        np.savetxt(filename, XYZ)

    def level_linewise(self):
        for i in range(self.Z.shape[0]):
            a, b = np.linalg.lstsq(np.vstack([self.X[i, :], np.ones(len(self.X[i, :]))]).T, self.Z[i, :], rcond=None)[0]
            self.Z[i, :] = self.Z[i, :] - self.X[i, :] * a - b

    def set_zero_level(self):
        min_z = np.min(self.Z)
        self.Z = self.Z - min_z

    def median(self, size):
        self.Z = Filters.median2d(self.Z, size)

    def mean(self, size):
        self.Z = Filters.mean2d(self.Z, size)

    def get_profile(self, start_point, end_point, width):
        profile = Curves.extract_profile(self.Z, start_point, end_point, width)
        dist=((self.X[start_point[0],start_point[1]]-self.X[end_point[0],end_point[1]])**2 +
              (self.Y[start_point[0],start_point[1]]-self.Y[end_point[0],end_point[1]])**2)**0.5
        distance = np.linspace(0, dist, num=len(profile))
        return distance, profile
