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
    class States:
        def __init__(self, data):
            self.states=[data]
            self.activeState = 0
            
        def undoPossible(self):
            if self.activeState > 0:
                return True
            else:
                return False
            
        def redoPossible(self):
            if self.activeState < len(self.states):
                return True
            else:
                return False
            
        def newState(self, data):
            if self.redoPossible():
                del self.states[self.activeState+1:]
            self.states.append(data)
            
                
            if len(self.states)>5:
                self.states.pop(0)
            self.activeState=len(self.states)
            
        def prevState(self):
            if self.undoPossible():
                self.activeState-=1
                return self.states[self.activeState]
            
        def nextState(self):
            if self.redoPossible():
                self.activeState+=1
                return self.states[self.activeState]
            

    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        self.parent=parent
        self.data=data
        self.winState = self.States(data)
        
              
        super(ResultWindow, self).__init__()
        
        # Creating figure canvas
        self.sc = FigureCanvas(self, width=width, height=height, dpi=dpi)
        # Ploting image in axes
        self.data.plotData(self.sc.axes)
        
        self.setCentralWidget(self.sc)
        #self.show()
        
        # Setting windown name
        if name==None:
            self.setWindowTitle(data.filename)
            
    def drawPlot(self):
        self.data.plotData(self.sc.axes)
        
    def undo(self):
        self.data=self.winState.prevState()
        
    def redo(self):
        self.data=self.winState.nextState()
    
    def modifyData(self, method):
        self.data=method()
        self.winState.newState(self.data)
        
        
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


class TopographyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        super().__init__(data, parent, width, height, dpi, name)
        self.show()

    
class SpectroscopyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        
        super().__init__(data, parent, width, height, dpi, name)
        self.show()
    
class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)
        
        
        