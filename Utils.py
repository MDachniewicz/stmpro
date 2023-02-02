# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 21:36:07 2023

@author: marek
"""

import matrixFileHandling as mfh
import Topography


def NewFile(file):
    mtrx = mfh.Matrix(file)
    if mtrx.filetype == 'Z':
        result = Topography.Topography(datatype='mtrx', data=mtrx)
                
    return result

    
def NewFileXYZ(files):
    for x in files:
        mtrx = mfh.Matrix(x)
        if mtrx.filetype == 'Z':
            result = Topography.Topography(mtrx)
        
            
    return result    