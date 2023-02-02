# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QLineEdit, QButtonGroup, QRadioButton, QMenu, QAction, QFileDialog,QLabel, QVBoxLayout, QWidget)
from PyQt5 import QtCore, QtWidgets


import Utils
from ResultWindow import ResultWindow


class MainWindow(QMainWindow):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        
        self.resultsWindows = []
        self.active_result_window=None
        
        
        
    def setupUi(self, MainWindow):
         MainWindow.setObjectName("STMpro")
         MainWindow.setWindowTitle("STMpro")
         MainWindow.resize(310, 80)
         self.centralwidget = QtWidgets.QWidget(MainWindow)
         self.centralwidget.setObjectName("central_widget")
         
    def _createMenuBar(self):
        menuBar = self.menuBar()
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.openXYZAction)
        fileMenu.addAction(self.saveXYZAction)
        fileMenu.addAction(self.exitAction)

        editMenu = menuBar.addMenu("&Edit")
        menuBar.addMenu(editMenu)
        editMenu.addAction(self.levelAction)
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.aboutAction)
        
    def _createActions(self):
        self.openAction = QAction("&Open mtrx...", self)
        self.openXYZAction = QAction("&Open XYZ...", self)
        self.saveXYZAction = QAction("&Save XYZ", self)
        self.exitAction = QAction("&Exit", self)
        
        self.levelAction = QAction("&Level", self)
        
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)
        
    def _connectActions(self):
        self.openAction.triggered.connect(self.openFile)
        self.openXYZAction.triggered.connect(self.openXYZFile)
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
        for file in files:
            data=Utils.NewFile(file)
            self.openResultWindow(data)
        
    def openXYZFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self,"QFileDialog.getOpenFileNames()", "","Z Matrix Files (*.xyz)", options=options)
        shape=[512, 512]
        for file in files:
            data=Utils.NewFileXYZ(file, shape)
            self.openResultWindow(data)
        
    def saveXYZFile(self):
        
        file, _ = QFileDialog.getSaveFileName(self)
        print(file)
        self.resultsWindows[self.active_result_window].data.saveXYZ(os.path.split(file)[1])
        print('Save clicked')
        
    def exitFile(self):
        self.close()  
        QtWidgets.qApp.quit()
          

    def levelEdit(self):
        data = self.resultsWindows[self.active_result_window].data
        data.level_linewise()
        self.openResultWindow(data)
        
    def aboutHelp(self):
        QtWidgets.QMessageBox.question(self,
        "About",
        "STMpro 0.0.2 test preview",
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
                for x in range(len(self.resultsWindows)):
                    self.resultsWindows.pop()
                    
        return False
    

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
                    

    def close_result(self, window):
        self.active_result_window = None
        self.resultsWindows.pop(self.resultsWindows.index(window))