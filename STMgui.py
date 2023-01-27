# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import sys, os, copy
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit, QButtonGroup, QRadioButton, QMenu, QAction, QFileDialog,QLabel, QVBoxLayout, QWidget)
from PyQt5 import QtCore, QtWidgets, QtGui
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

import GUIUtils
import matrixFileHandling as matrix
#import ResultWindow


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        
        self.resultsWindows = []
        self.a=1
        self.active_result_window=None
        self.active_result_window= None
        
        
    def setupUi(self, MainWindow):
         MainWindow.setObjectName("STMpro")
         MainWindow.setWindowTitle("STMpro")
         MainWindow.resize(310, 80)
         self.centralwidget = QtWidgets.QWidget(MainWindow)
         self.centralwidget.setObjectName("central_widget")
         
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveXYZAction)
        fileMenu.addAction(self.exitAction)

        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        menuBar.addMenu(editMenu)
        editMenu.addAction(self.levelAction)
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.aboutAction)
        
    def _createActions(self):
        # Creating action using the first constructor
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.saveXYZAction = QAction("&Save XYZ", self)
        self.exitAction = QAction("&Exit", self)
        
        self.levelAction = QAction("&Level", self)
        
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        
    def _connectActions(self):
        self.openAction.triggered.connect(self.openFile)
        self.saveXYZAction.triggered.connect(self.saveXYZFile)
        self.exitAction.triggered.connect(self.exitFile)
        self.levelAction.triggered.connect(self.levelEdit)
        self.aboutAction.triggered.connect(self.aboutHelp)
        

    def openResultWindow(self, result):
        win = ResultWindow(data=result, parent = self)
        self.resultsWindows.append(win)
        win.show()
                
    def openFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Z Matrix Files (*.Z_mtrx)", options=options)
        data=GUIUtils.NewFile(files)
        self.openResultWindow(data)
        
    def saveXYZFile(self):
        
        file, _ = QFileDialog.getSaveFileName(self)
        print(file)
        self.resultsWindows[self.active_result_window].data.saveXYZ(os.path.split(file)[1])
        print('Save clicked')
        
    def exitFile(self):
        self.close()    

    def levelEdit(self):
        print(self.resultsWindows[self.active_result_window])
        data = self.resultsWindows[self.active_result_window].data
        data.level_linewise()
        self.openResultWindow(data)
        
    def aboutHelp(self):
        QtWidgets.QMessageBox.question(self,
        "About",
        "STMpro 0.0.1 test preview",
        QtWidgets.QMessageBox.Ok)
        
    def event(self, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.on_window_activated(self)
        if event.type() == QtCore.QEvent.Close:
            print("Close clicked")
            answer = QtWidgets.QMessageBox.question(self,
            "Confirm Exit...",
            "Are you sure you want to exit?\nAll data will be lost.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            event.ignore()
            if answer == QtWidgets.QMessageBox.Yes:
                event.accept()
                for window in self.resultsWindows:
                    window.close()
        return False
    

         
#    def keyPressEvent(self, e): 
#        if e.key() == QtCore.Qt.Key_Escape:
#            self.close()
    def setActiveWindow(self, window):  
        self.active_result_window = self.resultsWindows.index(window)
        
    def on_window_activated(self, active_window):
        if active_window:
            if isinstance(active_window, ResultWindow):
                self.active_result_window = self.resultsWindows.index(active_window)
                print(self.active_result_window)
                
                #self.setActiveWindow(MainWindow, active_window)
                print("Aktywne okno:", active_window.windowTitle())

        else:
            print("Aktywne okno: Brak")
                    

        
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
        return False
    
class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)

    