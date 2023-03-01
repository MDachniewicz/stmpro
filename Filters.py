# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 21:16:07 2023

@author: marek
"""

from scipy import ndimage
import numpy as np


def median2d(data, size=3):
    return ndimage.median_filter(data, size)


def mean2d(data, size=3):
    kern = np.ones((size, size)) / (size * size)
    return ndimage.convolve(data, kern)
