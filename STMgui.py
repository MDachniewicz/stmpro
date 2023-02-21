# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import os

from PyQt5 import QtCore, QtWidgets, QtGui
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
        self._connect_push_buttons()
        self.installEventFilter(self)

        self.resultsWindows = []
        self.active_result_window = None
        self.interaction_mode = None
        # Creating filter window
        self.filterWin = FilterWindow(self)
        self.profileWin = ProfileWindow(self)
        #
        self._update_menu()
        self._update_push_buttons()
        self._updateWindows()
        
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("STMpro")
        MainWindow.setWindowTitle("STMpro")
        MainWindow.setFixedSize(310, 80)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("central_widget")

        #self.widget = QtWidgets.QWidget(self.centralwidget)
        #self.widget.setObjectName("widget")

        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName("gridLayout")

        self.openmtrxButton = QtWidgets.QPushButton(self.centralwidget)
        self.openmtrxButton.setObjectName("openmtrxbutton")
        self.openmtrxButton.setMinimumSize(QtCore.QSize(50, 50))
        self.openmtrxButton.setMaximumSize(QtCore.QSize(50, 50))
        self.openmtrxButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/open_mtrx.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openmtrxButton.setIcon(icon)
        self.openmtrxButton.setIconSize(QtCore.QSize(50, 50))
        self.gridLayout.addWidget(self.openmtrxButton, 0, 0 , 8,1)

        self.openxyzButton = QtWidgets.QPushButton(self.centralwidget)
        self.openxyzButton.setObjectName("openmtrxbutton")
        self.openxyzButton.setMinimumSize(QtCore.QSize(50, 50))
        self.openxyzButton.setMaximumSize(QtCore.QSize(50, 50))
        self.openxyzButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/open_xyz.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openxyzButton.setIcon(icon)
        self.openxyzButton.setIconSize(QtCore.QSize(50,50))
        self.gridLayout.addWidget(self.openxyzButton, 0, 1, 8, 1)

        self.undo_button = QtWidgets.QPushButton(self.centralwidget)
        self.undo_button.setObjectName("undo_button")
        self.undo_button.setMinimumSize(QtCore.QSize(50, 50))
        self.undo_button.setMaximumSize(QtCore.QSize(50, 50))
        self.undo_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/undo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.undo_button.setIcon(icon)
        self.undo_button.setIconSize(QtCore.QSize(50, 50))
        self.gridLayout.addWidget(self.undo_button, 0, 2, 8, 1)

        self.redo_button = QtWidgets.QPushButton(self.centralwidget)
        self.redo_button.setObjectName("redo_button")
        self.redo_button.setMinimumSize(QtCore.QSize(50, 50))
        self.redo_button.setMaximumSize(QtCore.QSize(50, 50))
        self.redo_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/redo.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.redo_button.setIcon(icon)
        self.redo_button.setIconSize(QtCore.QSize(50, 50))
        self.gridLayout.addWidget(self.redo_button, 0, 3, 8, 1)

        self.level_plane_button = QtWidgets.QPushButton(self.centralwidget)
        self.level_plane_button.setObjectName("Level_plane_button")
        self.level_plane_button.setMinimumSize(QtCore.QSize(50, 50))
        self.level_plane_button.setMaximumSize(QtCore.QSize(50, 50))
        self.level_plane_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/level.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.level_plane_button.setIcon(icon)
        self.level_plane_button.setIconSize(QtCore.QSize(50, 50))
        self.gridLayout.addWidget(self.level_plane_button, 0, 4, 8, 1)

        self.level_linewise_button = QtWidgets.QPushButton(self.centralwidget)
        self.level_linewise_button.setObjectName("Level_linewise_button")
        self.level_linewise_button.setMinimumSize(QtCore.QSize(50, 50))
        self.level_linewise_button.setMaximumSize(QtCore.QSize(50, 50))
        self.level_linewise_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("icons/level_linewise.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.level_linewise_button.setIcon(icon)
        self.level_linewise_button.setIconSize(QtCore.QSize(50, 50))
        self.gridLayout.addWidget(self.level_linewise_button, 0, 5, 8, 1)

        MainWindow.setCentralWidget(self.centralwidget)

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
        editMenu.addAction(self.level_planeAction)
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
        self.levelAction = QAction("&Level linewise", self)
        self.level_planeAction = QAction("&Level plane", self)
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
        self.level_planeAction.triggered.connect(self.level_planeEdit)
        self.filterAction.triggered.connect(self.filterEdit)
        self.profileAction.triggered.connect(self.profileEdit)
        
        self.aboutAction.triggered.connect(self.aboutHelp)

    def _connect_push_buttons(self):
        self.openmtrxButton.clicked.connect(self.openFile)
        self.openxyzButton.clicked.connect(self.openXYZFile)
        self.undo_button.clicked.connect(self.undoEdit)
        self.redo_button.clicked.connect(self.redoEdit)
        self.level_linewise_button.clicked.connect(self.levelEdit)
        self.level_plane_button.clicked.connect(self.level_planeEdit)
        
    def _update_push_buttons(self):
        if self.active_result_window == None:
            self.level_linewise_button.setDisabled(True)
            self.level_plane_button.setDisabled(True)
            self.undo_button.setDisabled(True)
            self.redo_button.setDisabled(True)
        
        else:
            active_window = self.resultsWindows[self.active_result_window]
            if isinstance(active_window, TopographyWindow):
                self.level_linewise_button.setDisabled(False)
                self.level_plane_button.setDisabled(False)
            if isinstance(active_window, SpectroscopyWindow):
                self.level_linewise_button.setDisabled(True)
                self.level_plane_button.setDisabled(True)
            if active_window.winState.undoPossible():
                self.undo_button.setDisabled(False)
            else:
                self.undo_button.setDisabled(True)
            if active_window.winState.redoPossible():
                self.redo_button.setDisabled(False)
            else:
                self.redo_button.setDisabled(True)

    def _update_menu(self):
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
            self.profileWin.clear_plot()
        else:
            active_window = self.resultsWindows[self.active_result_window]
            if isinstance(active_window, TopographyWindow):
                self.filterWin.enable()
                self.profileWin.enable()
                self.profileWin.update_plot()
            else:
                self.filterWin.disable()
                self.profileWin.disable()
                self.profileWin.clear_plot()


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
        self._update_menu()
        self._update_push_buttons()
        self._updateWindows()
        
    def redoEdit(self):
        result=self.resultsWindows[self.active_result_window]
        result.redo()
        self._update_menu()
        self._update_push_buttons()
        self._updateWindows()

    def levelEdit(self):
        if self.resultsWindows != []:
            result=self.resultsWindows[self.active_result_window]
            result.modifyData(result.data.level_linewise)
            self._update_menu()
            self._update_push_buttons()
            self._updateWindows()

    def level_planeEdit(self):
        if self.resultsWindows != []:
            result=self.resultsWindows[self.active_result_window]
            result.modifyData(result.data.level_plane)
            self._update_menu()
            self._update_push_buttons()
            self._updateWindows()

    def setZeroLevelEdit(self):
        result=self.resultsWindows[self.active_result_window]
        result.modifyData(result.data.set_zero_level)
        self._update_menu()
        self._update_push_buttons()
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
        self._update_menu()
        self._update_push_buttons()
        self._updateWindows()

    def on_window_activated(self, active_window):
        if active_window:
            if isinstance(active_window, ResultWindow):
                self.setActiveWindow(window=active_window)
            self._updateWindows()


    def close_result(self, window):
        self.setActiveWindow(close=True)
        self.resultsWindows.pop(self.resultsWindows.index(window))



    