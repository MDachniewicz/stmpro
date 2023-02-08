# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 21:36:07 2023

@author: marek
"""

import matrixFileHandling as mfh
import Topography
#import Exceptions

import numpy as np


def NewFile(file):

    mtrx = mfh.Matrix(file)
    if mtrx.filetype == 'Z':
        result = Topography.Topography(datatype='mtrx', data=mtrx)
    return result        
    
    
    

    
def NewFileXYZ(filename,shape):
    X=[]
    Y=[]
    Z=[]
        
    
    with open(filename, "r") as file:
        for line in file:
            x,y,z = line.split()
            X.append(float(x))
            Y.append(float(y))
            Z.append(float(z))
    X=np.array(X)
    X=np.reshape(X, shape)
    Y=np.array(Y)
    Y=np.reshape(Y, shape)
    Z=np.array(Z)
    Z=np.reshape(Z, shape)
    
    data=[X,Y,Z, filename]
    result = Topography.Topography(datatype='xyz', data=data)
        
            
    return result    