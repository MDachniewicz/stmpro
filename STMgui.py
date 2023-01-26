# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import sys, os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit, QButtonGroup, QRadioButton, QMenu, QAction, QFileDialog)
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
        
        self.resultsWindows = list()
        
    def setupUi(self, MainWindow):
         MainWindow.setObjectName("STMpro")
         MainWindow.resize(310, 80)
         self.centralwidget = QtWidgets.QWidget(MainWindow)
         self.centralwidget.setObjectName("central_widget")
         
    def _createMenuBar(self):
        menuBar = self.menuBar()
        # Creating menus using a QMenu object
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.newAction)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.saveAction)
        fileMenu.addAction(self.exitAction)

        # Creating menus using a title
        editMenu = menuBar.addMenu("&Edit")
        menuBar.addMenu(editMenu)
        fileMenu.addAction(self.levelAction)
        helpMenu = menuBar.addMenu("&Help")
    
        
    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        
        self.levelAction = QAction("&Level", self)
        
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.cutAction = QAction("C&ut", self)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        
    def _connectActions(self):
        self.openAction.triggered.connect(self.openFile)
        self.exitAction.triggered.connect(self.exitFile)

    def openResultWindow(self, result):
        win = ResultWindow1(data=result, parent=self)
        self.resultsWindows.append(win)
        win.show()
                
    def openFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        data=GUIUtils.NewFile(files)
        self.openResultWindow(data)
            

        
    def exitFile(self):
        self.close()
         
    def keyPressEvent(self, e): 
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()
            
class ResultWindow1(QMainWindow):
    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100): 
        self.parent=parent           
        super(ResultWindow1, self).__init__(parent)
        self.setupUi(self)    
        
    def setupUi(self, MainWindow):
         MainWindow.setObjectName("STMpro child")
         MainWindow.resize(310, 80)
         self.centralwidget = QtWidgets.QWidget(MainWindow)
         self.centralwidget.setObjectName("central_widget")
        
class ResultWindow(QMainWindow,FigureCanvasQTAgg):
    
    
    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100):
        self.parent=parent
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        data.plotData(self.axes)
        super(ResultWindow, self).__init__(fig)
   
    
    