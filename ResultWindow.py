# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:17:12 2023

@author: marek
"""
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import copy
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore



class ResultWindow(QMainWindow):
    data=None
    class States:
        def __init__(self, data):
            self.states=[data]
            self.activeState = 0
            
        def redoPossible(self):
            if self.activeState > 0:
                return True
            else:
                return False
            
        def undoPossible(self):
            if self.activeState < (len(self.states)-1):
                return True               
            else:
                return False
                
            
        def saveState(self, data):
            if self.redoPossible():
                self.states[0]=self.states[self.activeState]
                self.activeState=0
                del self.states[1:]
            data_cpy=copy.deepcopy(data)
            self.states.insert(1,data_cpy)
            #self.activeState
                
            if len(self.states)>5:
                self.states.pop(5)
            self.activeState=0
        def prevState(self):
            
            if self.undoPossible():
                self.activeState+=1
                return self.states[self.activeState]
            
        def nextState(self):
            if self.redoPossible():
                self.activeState-=1
                return self.states[self.activeState]
            

    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        self.parent=parent
        self.data=data
        self.winState = self.States(data)
        
        super(ResultWindow, self).__init__()
        self.installEventFilter(self)
        # Creating figure canvas
        self.canvas = FigureCanvasColorbar(self, width=width, height=height, dpi=dpi)
        self.setCentralWidget(self.canvas)
    
        # Setting windown name
        if name==None:
            self.setWindowTitle(data.filename)
            
    # Ploting image in axes        
    def drawPlot(self):

        self.canvas.fig.clf()
        axes = self.canvas.fig.add_subplot(111)
        im=axes.pcolor(self.data.X * 10 ** 9, self.data.Y * 10 ** 9, self.data.Z)
        self.canvas.fig.colorbar(im, ax=axes)
        self.canvas.draw()
        
        
    def undo(self):
        
        self.data=self.winState.prevState()
        self.drawPlot()
        
    def redo(self):
        self.data=self.winState.nextState()
        self.drawPlot()
    
    def modifyData(self, method):
        self.winState.saveState(self.data)
        method()
        self.drawPlot()
        
    # Event handling    
    def eventFilter(self, target, event):
        # Setting active result window if activated
        if event.type() == QtCore.QEvent.WindowActivate:
            self.parent.on_window_activated(self)
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Close:
            self.parent.close_result(self)
        return False


class TopographyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        super(TopographyWindow, self).__init__(data, parent, width, height, dpi, name)
        self.show()
        self.drawPlot()


    
class SpectroscopyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        super().__init__(data, parent, width, height, dpi, name)
        self.show()
    
class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)
        
class FigureCanvasColorbar(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super(FigureCanvasColorbar, self).__init__(self.fig)
        
        
        
        