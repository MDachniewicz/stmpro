# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import os

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QAction, QFileDialog)

import Utils
from ResultWindow import ResultWindow, SpectroscopyWindow, TopographyWindow
from FilterWindow import FilterWindow
from ProfileWindow import ProfileWindow


class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        self.installEventFilter(self)

        self.resultsWindows = []
        self.active_result_window = None
        self.interaction_mode = None
        # Creating filter window
        self.filterWin = FilterWindow(self)
        self.profileWin = ProfileWindow(self)
        #
        self._updateMenu()
        self._updateWindows()
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("STMpro")
        MainWindow.setWindowTitle("STMpro")
        MainWindow.setFixedSize(310, 80)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("central_widget")

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File Menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.openXYZAction)
        fileMenu.addAction(self.saveXYZAction)
        fileMenu.addAction(self.exitAction)
        # Edit Menu
        editMenu = menuBar.addMenu("&Edit")
        menuBar.addMenu(editMenu)        
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        editMenu.addAction(self.setZeroLevelAction)
        editMenu.addAction(self.levelAction)
        editMenu.addAction(self.filterAction)
        editMenu.addAction(self.profileAction)
        # Help Menu
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        #File
        self.openAction = QAction("&Open mtrx...", self)
        self.openXYZAction = QAction("&Open XYZ...", self)
        self.saveXYZAction = QAction("&Save XYZ", self)
        self.exitAction = QAction("&Exit", self)
        #Edit
        self.undoAction = QAction("&Undo", self)
        self.redoAction = QAction("&Redo", self)
        self.levelAction = QAction("&Level", self)
        self.setZeroLevelAction = QAction("&Set Zero Level", self)
        self.filterAction = QAction("&Filter...", self)
        self.profileAction = QAction("Profile...", self)
        #Help        
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

    def _connectActions(self):
        self.openAction.triggered.connect(self.openFile)
        self.openXYZAction.triggered.connect(self.openXYZFile)
        self.saveXYZAction.triggered.connect(self.saveXYZFile)
        self.exitAction.triggered.connect(self.exitFile)
        
        self.redoAction.triggered.connect(self.redoEdit)
        self.undoAction.triggered.connect(self.undoEdit)
        self.setZeroLevelAction.triggered.connect(self.setZeroLevelEdit)
        self.levelAction.triggered.connect(self.levelEdit)
        self.filterAction.triggered.connect(self.filterEdit)
        self.profileAction.triggered.connect(self.profileEdit)
        
        self.aboutAction.triggered.connect(self.aboutHelp)
        
    def _updateMenu(self):
        if self.active_result_window == None:
            self.levelAction.setDisabled(True)
            self.setZeroLevelAction.setDisabled(True)
            self.filterAction.setDisabled(True)
            self.profileAction.setDisabled(True)
            self.saveXYZAction.setDisabled(True)
            self.undoAction.setDisabled(True)
            self.redoAction.setDisabled(True)
        
        else:
            active_window = self.resultsWindows[self.active_result_window]
            if isinstance(active_window, TopographyWindow):
                self.levelAction.setDisabled(False)
                self.setZeroLevelAction.setDisabled(False)
                self.filterAction.setDisabled(False)
                self.profileAction.setDisabled(False)
                self.saveXYZAction.setDisabled(False)
            if isinstance(active_window, SpectroscopyWindow):
                self.levelAction.setDisabled(True)
                self.setZeroLevelAction.setDisabled(True)
                self.filterAction.setDisabled(True)
                self.profileAction.setDisabled(True)
                self.saveXYZAction.setDisabled(True)
            if active_window.winState.undoPossible():
                self.undoAction.setDisabled(False)
            else:
                self.undoAction.setDisabled(True)
            if active_window.winState.redoPossible():
                self.redoAction.setDisabled(False)
            else:
                self.redoAction.setDisabled(True)
                
                
    def _updateWindows(self):
        if self.active_result_window == None:
            self.filterWin.disable()
            self.profileWin.disable()
        else:
            active_window = self.resultsWindows[self.active_result_window]
            if isinstance(active_window, TopographyWindow):
                self.filterWin.enable()
                self.profileWin.enable()
            else:
                self.filterWin.disable()
                self.profileWin.disable()
            self.profileWin.update_plot()

    def openResultWindow(self, data, filetype):
        if filetype == 'Z' or filetype == 'I':
            win = TopographyWindow(data=data, parent=self)
        if filetype == 'I(V)-curve':
            win = SpectroscopyWindow(data=data, parent=self)
        self.resultsWindows.append(win)
        win.show()

    def openFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", "Z Matrix Files (*.Z_mtrx);;\
                                                I Matrix Files (*.I_mtrx);;\
                                                I(V) Matrix Files (*.I*V*_mtrx)",
                                                options=options)
        for file in files:
            try:
                data, filetype = Utils.NewFile(file)
                self.openResultWindow(data, filetype)
            except FileNotFoundError as e:
                if e.args[0] == "NoHeader":
                    QtWidgets.QMessageBox.question(self,
                                                   "Error",
                                                   "No header file (\"_0001.mtrx\") found.",
                                                   QtWidgets.QMessageBox.Ok)
    # Functions 
    def openXYZFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "", ".xyz Files (*.xyz)",
                                                options=options)
        ret, points, lines = self.getXYZsize()
        if ret == False:
            return
        shape = [points, lines]
        for file in files:
            try:
                data = Utils.NewFileXYZ(file, shape)
                self.openResultWindow(data, 'Z')
            except ValueError:
                QtWidgets.QMessageBox.question(self,
                                                "Error",
                                                "Wrong data dimensions.",
                                                QtWidgets.QMessageBox.Ok)

    def saveXYZFile(self):

        file, _ = QFileDialog.getSaveFileName(self)
        self.resultsWindows[self.active_result_window].data.saveXYZ(os.path.split(file)[1])

        
    def getXYZsize(self):
        dialog = QtWidgets.QInputDialog()
        dialog.setWindowTitle("XYZ size")
        dialog.setLabelText("Insert number of points and lines.")
        dialog.show()
        dialog.findChild(QtWidgets.QLineEdit).hide()
        inputs=[]
        input_points = QtWidgets.QLineEdit('0')
        inputs.append(input_points)
        input_lines = QtWidgets.QLineEdit('0')
        inputs.append(input_lines)
        dialog.layout().insertWidget(0, input_points)
        dialog.layout().insertWidget(1, input_lines)
        
        
        ret = dialog.exec_() == QtWidgets.QDialog.Accepted
        return ret, int(input_points.text()), int(input_lines.text())

    def exitFile(self):
        self.profileWin.close()
        self.filterWin.close()
        self.close()
        
    def undoEdit(self):
        result=self.resultsWindows[self.active_result_window]
        result.undo()
        self._updateMenu()
        self._updateWindows()
        
    def redoEdit(self):
        result=self.resultsWindows[self.active_result_window]
        result.redo()
        self._updateMenu()
        self._updateWindows()

    def levelEdit(self):
        result=self.resultsWindows[self.active_result_window]
        result.modifyData(result.data.level_linewise)
        self._updateMenu()
        self._updateWindows()

    def setZeroLevelEdit(self):
        result=self.resultsWindows[self.active_result_window]
        result.modifyData(result.data.set_zero_level)
        self._updateMenu()
        self._updateWindows()
        
    def filterEdit(self):
        self.filterWin.show()
        self._updateWindows()
        
    def profileEdit(self):
        self.profileWin.show()
        self.interaction_mode = 'profile'
        self._updateWindows()

    def aboutHelp(self):
        QtWidgets.QMessageBox.question(self,
                                       "About",
                                       "STMpro 0.0.5 pre-alpha",
                                       QtWidgets.QMessageBox.Ok)

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.on_window_activated(self)
        if event.type() == QtCore.QEvent.Close:
            answer = QtWidgets.QMessageBox.question(self,
                                                    "Confirm Exit...",
                                                    "Are you sure you want to exit?\nAll data will be lost.",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            event.ignore()
            if answer == QtWidgets.QMessageBox.Yes:
                event.accept()
                self.filterWin.close()
                self.profileWin.close()
                for x in range(len(self.resultsWindows)):
                    self.resultsWindows[0].close()

        return False

    def setActiveWindow(self, window = None, close = False):
        if close is False:
            self.active_result_window = self.resultsWindows.index(window)
        else:
            self.active_result_window = None
        self._updateMenu()
        self._updateWindows()

    def on_window_activated(self, active_window):
        if active_window:
            if isinstance(active_window, ResultWindow):
                self.setActiveWindow(window=active_window)

                if self.interaction_mode == 'profile':
                    self.profileWin.update_plot()


    def close_result(self, window):
        self.setActiveWindow(close=True)
        self.resultsWindows.pop(self.resultsWindows.index(window))



    