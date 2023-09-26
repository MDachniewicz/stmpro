# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 21:36:07 2023

@author: marek
"""

from src.stmpro.files import matrix_file_handling as mfh
from src.stmpro.data import topography
from src.stmpro.data import spectroscopy

import numpy as np


def NewFile(file):
    mtrx = mfh.Matrix(file)
    datatype = mtrx.datatype
    result_ref = None
    if datatype == 'Z' or datatype == 'I':
        result = Topography.Topography(filetype='mtrx', data=mtrx)
    if datatype == 'I(V)-curve':
        result = Spectroscopy.Spectroscopy(data=mtrx)
    if datatype == 'I(V)-map':
        result = Spectroscopy.SpectroscopyMap(data=mtrx)
        if mtrx.mtrxRef:
            result_ref = Topography.Topography(filetype='mtrx', data=mtrx.mtrxRef)

    return result, datatype, result_ref


def NewFileXYZ(filename, shape, unit):
    X = []
    Y = []
    Z = []

    with open(filename, "r") as file:
        for line in file:
            x, y, z = line.split()
            X.append(float(x))
            Y.append(float(y))
            Z.append(float(z))
    if shape == [0, 0]:
        size = int(len(X) ** 0.5)
        shape = [size, size]
    X = np.array(X)
    X = np.reshape(X, shape)
    Y = np.array(Y)
    Y = np.reshape(Y, shape)
    Z = np.array(Z)
    Z = np.reshape(Z, shape)

    data = [X, Y, Z, filename]
    result = Topography.Topography(filetype='xyz', data=data, unit=unit)

    return result
