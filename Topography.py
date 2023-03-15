# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 20:58:54 2023

@author: marek
"""
import os
import numpy as np
import itertools
from STMData import STMData
import Filters
import Curves
import Images
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


class Topography(STMData):
    AXES = ['Forward-Up', 'Backward-Up', 'Forward-Down', 'Backward-Down']

    def __init__(self, filetype, data, unit='m', ax=0):
        self.name = None
        self.available_axes = []
        self.active_ax = ax
        self.z_data = []
        if filetype == 'mtrx':
            self.__initMtrx(data, ax)

        if filetype == 'xyz':
            self.__initXYZ(data, unit)

        self.X, self.xunit = self.auto_set_unit(self.X, self.xunit)
        self.Y = self.set_unit(self.Y, self.yunit, self.xunit)
        self.yunit = self.xunit

        #for enum, z in enumerate(self.z_data):
        #    if self.available_axes[enum]:
        #        self.z_data[enum], self.unit = self.auto_set_unit(z, self.unit)

        self.Z, self.unit = self.update_unit(self.Z, self.unit)

    def __initMtrx(self, mtrx, ax):
        self.datatype = mtrx.datatype
        self.parameters = mtrx.parameter
        self.X = mtrx.x
        self.Y = mtrx.y
        _, self.filename = os.path.split(mtrx.file)
        self.xunit = 'm'
        self.yunit = 'm'
        self.active_ax = 0
        self.z_data.append(mtrx.imageForwUp)
        self.z_data.append(mtrx.imageBackUp)
        self.z_data.append(mtrx.imageForwDown)
        self.z_data.append(mtrx.imageBackDown)
        self._available_axes()
        self.change_ax(ax=None)
        if self.datatype == 'Z':
            self.__initMtrxZ(mtrx, ax)
        if self.datatype == 'I':
            self.__initMtrxI(mtrx, ax)

    def __initMtrxZ(self, mtrx, ax=None):
        self.unit = 'm'
        self.name = f'Topography Image ({self.AXES[self.active_ax]}): {self.filename}'
        self.set_zero_level()

    def __initMtrxI(self, mtrx, ax=None):
        self.unit = 'A'
        self.name = f'Current Image ({self.AXES[self.active_ax]}): {self.filename}'

    def __initXYZ(self, data, unit):
        self.X = data[0]
        self.Y = data[1]
        self.Z = data[2]
        self.unit = unit
        self.xunit = unit
        self.yunit = unit
        self.filename = data[3]

    def _available_axes(self):
        for x in self.z_data:
            if x == []:
                self.available_axes.append(False)
            else:
                self.available_axes.append(True)

    def change_ax(self, ax=None):
        if ax is None:
            for enum, x in enumerate(self.available_axes):
                if x != 0:
                    self.Z = self.z_data[enum]
                    self.active_ax = enum
                    return
        else:
            self.Z, si_unit  = self.unit_to_si(self.Z, self.unit)
            self.Z, self.z_data[self.active_ax] = self.z_data[ax], self.Z
            self.active_ax = ax
            self.Z, self.unit = self.update_unit(self.Z, si_unit)
            if self.datatype == 'Z':
                self.name = f'Topography Image ({self.AXES[self.active_ax]}): {self.filename}'
            if self.datatype == 'I':
                self.name = f'Current Image ({self.AXES[self.active_ax]}): {self.filename}'
                
    def plotData(self, ax=None):
        if ax:
            im = ax.pcolor(self.X * 10 ** 9, self.Y * 10 ** 9, self.Z)
            divider = make_axes_locatable(ax)
            cax = divider.append_axes("right", size="5%", pad=0.05)
            ax.axis('equal')
            plt.colorbar(im, cax=cax)

    def XYZ(self):
        x, _ = self.unit_to_si(self.X, self.xunit)
        y, _ = self.unit_to_si(self.Y, self.yunit)
        z, _ = self.unit_to_si(self.Z, self.unit)

        return np.hstack([x.reshape(-1, 1), y.reshape(-1, 1), z.reshape(-1, 1)])

    def saveXYZ(self, filename=None):
        if filename == None:
            filename = self.filename + '.xyz'
        if filename[-3:] != 'xyz':
            filename = filename + '.xyz'
        XYZ = self.XYZ()
        np.savetxt(filename, XYZ)

    # Leveling
    def level_linewise(self):
        for i in range(self.Z.shape[0]):
            a, b = np.linalg.lstsq(np.vstack([self.X[i, :], np.ones(len(self.X[i, :]))]).T, self.Z[i, :], rcond=None)[0]
            self.Z[i, :] = self.Z[i, :] - self.X[i, :] * a - b
        self.Z, self.unit = self.update_unit(self.Z, self.unit)

    def level_plane(self):
        x = self.X.reshape((-1,))
        y = self.Y.reshape((-1,))
        z = self.Z.reshape((-1,))

        def polyfit2d(x, y, z, order=1):
            ncols = (order + 1) ** 2
            G = np.zeros((x.size, ncols))
            ij = itertools.product(range(order + 1), range(order + 1))
            for k, (i, j) in enumerate(ij):
                G[:, k] = x ** i * y ** j
            m, _, _, _ = np.linalg.lstsq(G, z, rcond=None)
            return m

        def polyval2d(x, y, m):
            order = int(np.sqrt(len(m))) - 1
            ij = itertools.product(range(order + 1), range(order + 1))
            z = np.zeros_like(x)
            for a, (i, j) in zip(m, ij):
                z += a * x ** i * y ** j
            return z

        m = polyfit2d(x, y, z)
        z = polyval2d(z, y, m)
        z = z.reshape((self.Z.shape))

        self.Z = self.Z - z
        self.Z, self.unit = self.update_unit(self.Z, self.unit)

    def get_z_range(self):
        min = np.amin(self.Z)
        max = np.amax(self.Z)
        range = max - min
        return range

    def get_x_range(self):
        min = np.amin(self.X)
        max = np.amax(self.X)
        range = max - min
        return range

    def get_y_range(self):
        min = np.amin(self.Y)
        max = np.amax(self.Y)
        range = max - min
        return range

    def get_units(self):
        return self.unit, self.xunit, self.yunit

    # Basic operations
    def set_zero_level(self):
        min_z = np.min(self.Z)
        self.Z = self.Z - min_z

    def change_level(self, z):
        self.Z += z

    def scale(self, factors):
        self.X = self.X * factors[0]
        self.Y = self.Y * factors[1]
        self.Z = self.Z * factors[2]
        self.Z, self.unit = self.update_unit(self.Z, self.unit)
        self.X, self.xunit = self.update_unit(self.X, self.xunit)
        self.Y = self.set_unit(self.Y, self.yunit, self.xunit)
        self.yunit = self.xunit

    def mirror_ud(self):
        self.Z = np.flipud(self.Z)

    def mirror_lr(self):
        self.Z = np.fliplr(self.Z)

    def rotate90(self, k):
        self.Z = np.rot90(self.Z, k)
        if k % 2 != 0:
            self.X, self.Y = np.rot90(self.Y), np.rot90(self.X, 3)

    # Filtering
    def median(self, size):
        self.Z = Filters.median2d(self.Z, size)
        self.Z, self.unit = self.update_unit(self.Z, self.unit)

    def mean(self, size):
        self.Z = Filters.mean2d(self.Z, size)
        self.Z, self.unit = self.update_unit(self.Z, self.unit)

    # Measure profile
    def get_profile(self, start_point, end_point, width):
        profile = Curves.extract_profile(self.Z, start_point, end_point, width)
        dist = ((self.X[start_point[0], start_point[1]] - self.X[end_point[0], end_point[1]]) ** 2 +
                (self.Y[start_point[0], start_point[1]] - self.Y[end_point[0], end_point[1]]) ** 2) ** 0.5
        distance = np.linspace(0, dist, num=len(profile))
        return distance, profile

    # Histogram
    def histogram(self, n_bins):
        z = self.Z.reshape(-1, 1)
        hist, bin_edges = np.histogram(z, n_bins)
        return hist, bin_edges

    # FFT
    def fft(self):
        return Images.fft_image(self.Z)

    def ifft(self, fft_image):
        return Images.ifft_image(fft_image)


class ProfileData(STMData):
    def __init__(self, distance, profile, xunit, unit, name=None):
        self.distance = distance
        self.profile = profile
        self.filename = name
        self.unit = unit
        self.xunit = xunit

    def auto_units(self):
        self.distance, self.xunit = self.update_unit(self.distance, self.xunit)
        self.profile, self.unit = self.update_unit(self.profile, self.unit)

    def set_profile_units(self, xunit, unit):
        if not self.unit == unit:
            self.profile = self.set_unit(self.profile, self.unit, unit)
            self.unit = unit
        if not self.xunit == xunit:
            self.distance = self.set_unit(self.distance, self.xunit, xunit)
            self.xunit = xunit

    def get_range(self):
        return np.ptp(self.unit_to_si(self.profile, self.unit)[0])

    def get_xrange(self):
        return np.ptp(self.unit_to_si(self.distance, self.xunit)[0])
