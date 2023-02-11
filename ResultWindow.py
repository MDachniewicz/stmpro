# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:17:12 2023

@author: marek
"""
import matplotlib
matplotlib.use('Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore



class ResultWindow(QMainWindow):


    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        self.parent=parent
        self.data=data
              
        super(ResultWindow, self).__init__()
        
        # Creating figure canvas
        sc = FigureCanvas(self, width=width, height=height, dpi=dpi)
        # Ploting image in axes
        data.plotData(sc.axes)
        
        self.setCentralWidget(sc)
        self.show()
        
        # Setting windown name
        if name==None:
            self.setWindowTitle(data.filename)
        
        
    # Event handling    
    def event(self, event):
        # Setting active result window if activated
        if event.type() == QtCore.QEvent.WindowActivate:
            self.parent.on_window_activated(self)
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Close:
            print("Close clicked")
            self.parent.close_result(self)
        return False
    
class SpectroscopyWindow(QMainWindow):
    def __init__(self, data=None, parent=None, width=6, height=3, dpi=100, name=None):
        
        self.parent=parent
        self.data=data
              
        super(ResultWindow, self).__init__()        
        # Creating figure canvas
        sc = FigureCanvas(self, width=width, height=height, dpi=dpi)
        # Ploting image in axes
        data.plotData(sc.axes)        
        self.setCentralWidget(sc)
        self.show()        
        # Setting windown name
        if name==None:
            self.setWindowTitle(data.filename)
        
        
    # Event handling    
    def event(self, event):
        # Setting active result window if activated
        if event.type() == QtCore.QEvent.WindowActivate:
            self.parent.on_window_activated(self)
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Close:
            print("Close clicked")
            self.parent.close_result(self)
        return False
    
class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)
        
        
        