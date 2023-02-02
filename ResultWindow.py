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


    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100):
        self.parent=parent
        self.data=data
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        data.plotData(self.axes)
        super(ResultWindow, self).__init__()
        self.setWindowTitle(data.filename)
        
        sc = FigureCanvas(width=5, height=4, dpi=100)
        data.plotData(sc.axes)
        self.setCentralWidget(sc)
        self.show()
        
    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.parent.on_window_activated(self)
        if event.type() == QtCore.QEvent.Close:
            print("Close clicked")
            self.parent.close_result(self)
        return False
    
class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)