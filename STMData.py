# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 21:05:15 2023

@author: marek
"""

class STMData:
    file_name=None
    parameters={}
    comment={}
    data_type=None
    unit=None
    
    def __init__(self):
        pass
    
    def __repr__(self):
        if self.data_type=='Z':
            return 'Topography image'
        else:
            return 'No data'