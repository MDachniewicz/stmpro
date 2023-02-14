# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 21:05:15 2023

@author: marek
"""

class STMData:
    filename=None
    parameters={}
    comment={}
    filetype=None
    unit=None
    
    def __init__(self):
        pass
    
    def __repr__(self):
        if self.filetype=='Z':
            return 'Topography image'
        else:
            return 'No data'