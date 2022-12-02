# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import sys, os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit, QButtonGroup, QRadioButton, QMenu, QAction, QFileDialog)
from PyQt5 import QtCore, QtWidgets, QtGui
import matrixFileHandling as matrix


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        
    def setupUi(self, MainWindow):
         MainWindow.setObjectName("STM pro")
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
        helpMenu = menuBar.addMenu("&Help")
    
        
    def _createActions(self):
        # Creating action using the first constructor
        self.newAction = QAction(self)
        self.newAction.setText("&New")
        # Creating actions using the second constructor
        self.openAction = QAction("&Open...", self)
        self.saveAction = QAction("&Save", self)
        self.exitAction = QAction("&Exit", self)
        self.copyAction = QAction("&Copy", self)
        self.pasteAction = QAction("&Paste", self)
        self.cutAction = QAction("C&ut", self)
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        
    def _connectActions(self):
        self.openAction.triggered.connect(self.openFile)
        self.exitAction.triggered.connect(self.exitFile)
        
    def openFile(self):
        print("OpenFile Pressed")
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","All Files (*);;Python Files (*.py)", options=options)
        print(files)
        for x in files:
            head, tail = os.path.split(x)
            print(head)
            print(tail)
            mtrx=matrix.Matrix(tail)
            mtrx.show()
            
        
    def exitFile(self):
        self.close()
         
    def keyPressEvent(self, e): 
        if e.key() == QtCore.Qt.Key_Escape:
            self.close()