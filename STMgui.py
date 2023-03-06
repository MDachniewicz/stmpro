# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:41:45 2022

@author: marek
"""

import os, sys

from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtWidgets import (QMainWindow, QMenu,
                             QAction, QFileDialog, QActionGroup)

import Files
from ResultWindow import ResultWindow, SpectroscopyWindow, TopographyWindow
from FilterWindow import FilterWindow
from ProfileWindow import ProfileWindow
from HistogramWindow import HistogramWindow
from FourierWindow import FourierWindow
from ScaleWindow import ScaleWindow
from ExportWindow import ExportWindow

def resources_path(path):
    try:
        return os.path.join(sys._MEIPASS, path)
    except:
        return path

class MainWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self._createActions()
        self._createMenuBar()
        self._connectActions()
        self._connect_push_buttons()
        self.installEventFilter(self)

        self.results_windows = []  # Array of active results windows
        self.active_result_window = None  # Variable keeping index of active result window
        self.interaction_mode = None  # Active interaction mode
        # Keeping track of active windows, to know if we should update them
        self.profile_win_active = False
        self.filter_win_active = False
        self.hist_win_active = False
        self.fft_win_active = False
        self.scale_win_active = False
        # Creating processing windows
        self.filterWin = FilterWindow(self)
        self.profileWin = ProfileWindow(self)
        self.hist_win = HistogramWindow(self)
        self.fft_win = FourierWindow(self)
        self.scale_win = ScaleWindow(self)
        self.export_win = ExportWindow(self)
        # First update of menus, buttons and windows
        self._update_menu()
        self._update_push_buttons()
        self.update_windows()

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("STMpro")
        MainWindow.setWindowTitle("STMpro")
        MainWindow.setFixedSize(310, 200)
        button_size = 40
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("central_widget")

        self.vertical_layout = QtWidgets.QVBoxLayout(self.centralwidget)

        self.grid_layout1 = QtWidgets.QGridLayout(self.centralwidget)
        self.grid_layout1.setObjectName("Files Operations")

        self.grid_layout2 = QtWidgets.QGridLayout(self.centralwidget)
        self.grid_layout2.setObjectName("Topography")
        #self.grid_layout2.setHorizontalSpacing(10)
        #self.grid_layout2.setVerticalSpacing(80)
        #self.grid_layout2.setContentsMargins(11, 11, 11, 11)
        #self.grid_layout2.setSpacing(60)


        #self.label1 = QtWidgets.QLabel(self.centralwidget, text='Files')
        self.label2 = QtWidgets.QLabel(self.centralwidget, text='Topography')
        self.label2.setMinimumSize(QtCore.QSize(200,20))
        self.label2.setMaximumSize(QtCore.QSize(200,20))
        #self.vertical_layout.addWidget(self.label1)
        self.vertical_layout.addLayout(self.grid_layout1)

        self.vertical_layout.addWidget(self.label2)
        self.vertical_layout.addLayout(self.grid_layout2)

        self.openmtrxButton = QtWidgets.QPushButton(self.centralwidget)
        self.openmtrxButton.setObjectName("openmtrxbutton")
        self.openmtrxButton.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.openmtrxButton.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.openmtrxButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/open_mtrx.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openmtrxButton.setIcon(icon)
        self.openmtrxButton.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout1.addWidget(self.openmtrxButton, 0, 0, 1, 1)

        self.openxyzButton = QtWidgets.QPushButton(self.centralwidget)
        self.openxyzButton.setObjectName("openmtrxbutton")
        self.openxyzButton.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.openxyzButton.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.openxyzButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/open_xyz.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.openxyzButton.setIcon(icon)
        self.openxyzButton.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout1.addWidget(self.openxyzButton, 0, 1, 1, 1)

        self.undo_button = QtWidgets.QPushButton(self.centralwidget)
        self.undo_button.setObjectName("undo_button")
        self.undo_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.undo_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.undo_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/undo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.undo_button.setIcon(icon)
        self.undo_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout1.addWidget(self.undo_button, 0, 2, 1, 1)

        self.redo_button = QtWidgets.QPushButton(self.centralwidget)
        self.redo_button.setObjectName("redo_button")
        self.redo_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.redo_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.redo_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/redo.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.redo_button.setIcon(icon)
        self.redo_button.setIconSize(QtCore.QSize(50, 50))
        self.grid_layout1.addWidget(self.redo_button, 0, 3, 1, 1)

        self.set_zero_button = QtWidgets.QPushButton(self.centralwidget)
        self.set_zero_button.setObjectName("Set_zeto_button")
        self.set_zero_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.set_zero_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.set_zero_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/set_zero.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.set_zero_button.setIcon(icon)
        self.set_zero_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.set_zero_button, 0, 0, 1, 1)

        self.profile_button = QtWidgets.QPushButton(self.centralwidget)
        self.profile_button.setObjectName("Profile_button")
        self.profile_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.profile_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.profile_button.setText("")
        self.profile_button.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/profile.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.profile_button.setIcon(icon)
        self.profile_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.profile_button, 0, 1, 1, 1)

        self.level_plane_button = QtWidgets.QPushButton(self.centralwidget)
        self.level_plane_button.setObjectName("Level_plane_button")
        self.level_plane_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.level_plane_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.level_plane_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/level.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.level_plane_button.setIcon(icon)
        self.level_plane_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.level_plane_button, 0, 2, 1, 1)

        self.level_linewise_button = QtWidgets.QPushButton(self.centralwidget)
        self.level_linewise_button.setObjectName("Level_linewise_button")
        self.level_linewise_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.level_linewise_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.level_linewise_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/level_linewise.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.level_linewise_button.setIcon(icon)
        self.level_linewise_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.level_linewise_button, 0, 3, 1, 1)

        self.filter_button = QtWidgets.QPushButton(self.centralwidget)
        self.filter_button.setObjectName("filter_button")
        self.filter_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.filter_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.filter_button.setText("")
        self.filter_button.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/filter.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.filter_button.setIcon(icon)
        self.filter_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.filter_button, 0, 4, 1, 1)

        self.fft_button = QtWidgets.QPushButton(self.centralwidget)
        self.fft_button.setObjectName("fft_button")
        self.fft_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.fft_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.fft_button.setText("")
        self.fft_button.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/fft.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.fft_button.setIcon(icon)
        self.fft_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.fft_button, 0, 5, 1, 1)

        self.rotate_clockwise_button = QtWidgets.QPushButton(self.centralwidget)
        self.rotate_clockwise_button.setObjectName("rotate_clockwise_button")
        self.rotate_clockwise_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.rotate_clockwise_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.rotate_clockwise_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/rotate_clockwise.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rotate_clockwise_button.setIcon(icon)
        self.rotate_clockwise_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.rotate_clockwise_button, 1, 0, 1, 1)

        self.rotate_anticlockwise_button = QtWidgets.QPushButton(self.centralwidget)
        self.rotate_anticlockwise_button.setObjectName("rotate_anticlockwise_button")
        self.rotate_anticlockwise_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.rotate_anticlockwise_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.rotate_anticlockwise_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/rotate_anticlockwise.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.rotate_anticlockwise_button.setIcon(icon)
        self.rotate_anticlockwise_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.rotate_anticlockwise_button, 1, 1, 1, 1)

        self.vertical_mirror_button = QtWidgets.QPushButton(self.centralwidget)
        self.vertical_mirror_button.setObjectName("vertical_mirror_button")
        self.vertical_mirror_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.vertical_mirror_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.vertical_mirror_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/vertical_mirror.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.vertical_mirror_button.setIcon(icon)
        self.vertical_mirror_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.vertical_mirror_button, 1, 2, 1, 1)

        self.horizontal_mirror_button = QtWidgets.QPushButton(self.centralwidget)
        self.horizontal_mirror_button.setObjectName("horizontal_mirror_button")
        self.horizontal_mirror_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.horizontal_mirror_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.horizontal_mirror_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/horizontal_mirror.png")), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.horizontal_mirror_button.setIcon(icon)
        self.horizontal_mirror_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.horizontal_mirror_button, 1, 3, 1, 1)

        self.scale_button = QtWidgets.QPushButton(self.centralwidget)
        self.scale_button.setObjectName("Scale_button")
        self.scale_button.setMinimumSize(QtCore.QSize(button_size, button_size))
        self.scale_button.setMaximumSize(QtCore.QSize(button_size, button_size))
        self.scale_button.setText("")
        self.scale_button.setCheckable(True)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(resources_path("icons/scale.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.scale_button.setIcon(icon)
        self.scale_button.setIconSize(QtCore.QSize(button_size, button_size))
        self.grid_layout2.addWidget(self.scale_button, 1, 4, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)

    def _createMenuBar(self):
        menuBar = self.menuBar()
        # File Menu
        fileMenu = QMenu("&File", self)
        menuBar.addMenu(fileMenu)
        fileMenu.addAction(self.openAction)
        fileMenu.addAction(self.openXYZAction)
        fileMenu.addAction(self.saveXYZAction)
        fileMenu.addAction(self.save_png_action)
        fileMenu.addAction(self.export_action)
        fileMenu.addAction(self.exitAction)
        # Edit Menu
        editMenu = menuBar.addMenu("&Edit")
        menuBar.addMenu(editMenu)
        editMenu.addAction(self.undoAction)
        editMenu.addAction(self.redoAction)
        editMenu.addSeparator()
        basic_operations_menu = editMenu.addMenu("&Basic Operations")
        basic_operations_menu.addAction(self.scale_action)
        basic_operations_menu.addAction(self.rotate_clockwise_action)
        basic_operations_menu.addAction(self.rotate_anticlockwise_action)
        basic_operations_menu.addAction(self.mirror_ud_action)
        basic_operations_menu.addAction(self.mirror_lr_action)

        leveling_menu = editMenu.addMenu("&Leveling")
        editMenu.addAction(self.setZeroLevelAction)
        leveling_menu.addAction(self.levelAction)
        leveling_menu.addAction(self.level_planeAction)
        editMenu.addAction(self.filterAction)
        editMenu.addAction(self.profileAction)
        editMenu.addAction(self.histAction)
        editMenu.addAction(self.fft_action)
        #Topography Menu
        topography_menu = menuBar.addMenu("&Topography")
        select_ax_menu = topography_menu.addMenu("&Select image")
        select_ax_menu.addAction(self.change_image1_action)
        select_ax_menu.addAction(self.change_image2_action)
        select_ax_menu.addAction(self.change_image3_action)
        select_ax_menu.addAction(self.change_image4_action)
        # Help Menu
        helpMenu = menuBar.addMenu("&Help")
        helpMenu.addAction(self.aboutAction)

    def _createActions(self):
        # File
        self.openAction = QAction("&Open mtrx...", self)
        self.openXYZAction = QAction("&Open XYZ...", self)
        self.saveXYZAction = QAction("&Save XYZ", self)
        self.save_png_action = QAction("&Save PNG", self)
        self.export_action = QAction("&Export", self)
        self.exitAction = QAction("&Exit", self)
        # Edit
        self.undoAction = QAction("&Undo", self)
        self.redoAction = QAction("&Redo", self)

        self.scale_action = QAction("&Scale...", self)
        self.rotate_clockwise_action = QAction("&Rotate clockwise 90°", self)
        self.rotate_anticlockwise_action = QAction("&Rotate anti-clockwise 90°", self)
        self.mirror_ud_action = QAction("&Horizontal mirror", self)
        self.mirror_lr_action = QAction("&Vertical mirror", self)

        self.levelAction = QAction("&Level linewise", self)
        self.level_planeAction = QAction("&Level plane", self)
        self.setZeroLevelAction = QAction("&Set Zero Level", self)
        self.filterAction = QAction("&Filter...", self)
        self.profileAction = QAction("Profile...", self)
        self.histAction = QAction("Histogram...", self)
        self.fft_action = QAction("FFT...", self)
        # Topography
        # Scanning direction selection
        self.change_image_group = QActionGroup(self)
        self.change_image1_action = QAction("&Forward-Up", self)
        self.change_image2_action = QAction("&Backward-Up", self)
        self.change_image3_action = QAction("&Forward-Down", self)
        self.change_image4_action = QAction("&Backward-Down", self)
        self.change_image1_action.setCheckable(True)
        self.change_image2_action.setCheckable(True)
        self.change_image3_action.setCheckable(True)
        self.change_image4_action.setCheckable(True)
        self.change_image_group.addAction(self.change_image1_action)
        self.change_image_group.addAction(self.change_image2_action)
        self.change_image_group.addAction(self.change_image3_action)
        self.change_image_group.addAction(self.change_image4_action)
        # Help
        self.helpContentAction = QAction("&Help Content", self)
        self.aboutAction = QAction("&About", self)

    def _connectActions(self):
        self.openAction.triggered.connect(self.openFile)
        self.openXYZAction.triggered.connect(self.openXYZFile)
        self.saveXYZAction.triggered.connect(self.saveXYZFile)
        self.save_png_action.triggered.connect(self.save_png)
        self.export_action.triggered.connect(self.export)
        self.exitAction.triggered.connect(self.exitFile)

        self.redoAction.triggered.connect(self.redoEdit)
        self.undoAction.triggered.connect(self.undoEdit)
        self.scale_action.triggered.connect(self.scale)
        self.rotate_clockwise_action.triggered.connect(self.rotate_clockwise)
        self.rotate_anticlockwise_action.triggered.connect(self.rotate_anticlockwise)
        self.mirror_ud_action.triggered.connect(self.mirror_ud)
        self.mirror_lr_action.triggered.connect(self.mirror_lr)
        self.setZeroLevelAction.triggered.connect(self.setZeroLevelEdit)
        self.levelAction.triggered.connect(self.levelEdit)
        self.level_planeAction.triggered.connect(self.level_planeEdit)
        self.filterAction.triggered.connect(self.filterEdit)
        self.profileAction.triggered.connect(self.profileEdit)
        self.histAction.triggered.connect(self.hist_edit)
        self.fft_action.triggered.connect(self.fft_edit)

        self.change_image1_action.triggered.connect(self.change_image)
        self.change_image2_action.triggered.connect(self.change_image)
        self.change_image3_action.triggered.connect(self.change_image)
        self.change_image4_action.triggered.connect(self.change_image)

        self.aboutAction.triggered.connect(self.aboutHelp)

    def _connect_push_buttons(self):
        self.openmtrxButton.clicked.connect(self.openFile)
        self.openxyzButton.clicked.connect(self.openXYZFile)
        self.undo_button.clicked.connect(self.undoEdit)
        self.redo_button.clicked.connect(self.redoEdit)
        self.level_linewise_button.clicked.connect(self.levelEdit)
        self.level_plane_button.clicked.connect(self.level_planeEdit)
        self.set_zero_button.clicked.connect(self.setZeroLevelEdit)
        self.profile_button.clicked.connect(self.profileEdit)
        self.scale_button.clicked.connect(self.scale)
        self.filter_button.clicked.connect(self.filterEdit)
        self.fft_button.clicked.connect(self.fft_edit)
        self.rotate_anticlockwise_button.clicked.connect(self.rotate_anticlockwise)
        self.rotate_clockwise_button.clicked.connect(self.rotate_clockwise)
        self.vertical_mirror_button.clicked.connect(self.mirror_lr)
        self.horizontal_mirror_button.clicked.connect(self.mirror_ud)

    def _update_push_buttons(self):
        if self.active_result_window == None:
            self.level_linewise_button.setDisabled(True)
            self.level_plane_button.setDisabled(True)
            self.undo_button.setDisabled(True)
            self.redo_button.setDisabled(True)
            self.set_zero_button.setDisabled(True)
            self.profile_button.setDisabled(True)
            self.scale_button.setDisabled(True)
            self.rotate_clockwise_button.setDisabled(True)
            self.rotate_anticlockwise_button.setDisabled(True)
            self.vertical_mirror_button.setDisabled(True)
            self.horizontal_mirror_button.setDisabled(True)
            self.filter_button.setDisabled(True)
            self.fft_button.setDisabled(True)

        else:
            active_window = self.results_windows[self.active_result_window]
            if isinstance(active_window, TopographyWindow):
                self.level_linewise_button.setDisabled(False)
                self.level_plane_button.setDisabled(False)
                self.set_zero_button.setDisabled(False)
                self.profile_button.setDisabled(False)
                self.scale_button.setDisabled(False)
                self.rotate_clockwise_button.setDisabled(False)
                self.rotate_anticlockwise_button.setDisabled(False)
                self.vertical_mirror_button.setDisabled(False)
                self.horizontal_mirror_button.setDisabled(False)
                self.filter_button.setDisabled(False)
                self.fft_button.setDisabled(False)

            if isinstance(active_window, SpectroscopyWindow):
                self.level_linewise_button.setDisabled(True)
                self.level_plane_button.setDisabled(True)
                self.set_zero_button.setDisabled(True)
                self.profile_button.setDisabled(True)
                self.scale_button.setDisabled(True)
                self.rotate_clockwise_button.setDisabled(True)
                self.rotate_anticlockwise_button.setDisabled(True)
                self.vertical_mirror_button.setDisabled(True)
                self.horizontal_mirror_button.setDisabled(True)
                self.filter_button.setDisabled(True)
                self.fft_button.setDisabled(True)

            if active_window.winState.undoPossible():
                self.undo_button.setDisabled(False)
            else:
                self.undo_button.setDisabled(True)
            if active_window.winState.redoPossible():
                self.redo_button.setDisabled(False)
            else:
                self.redo_button.setDisabled(True)

    def _update_menu(self):
        for button in self.change_image_group.actions():
            button.setChecked(False)
        if self.active_result_window == None:
            self.rotate_clockwise_action.setDisabled(True)
            self.rotate_anticlockwise_action.setDisabled(True)
            self.mirror_ud_action.setDisabled(True)
            self.mirror_lr_action.setDisabled(True)
            self.levelAction.setDisabled(True)
            self.level_planeAction.setDisabled(True)
            self.setZeroLevelAction.setDisabled(True)
            self.filterAction.setDisabled(True)
            self.profileAction.setDisabled(True)
            self.histAction.setDisabled(True)
            self.fft_action.setDisabled(True)
            self.scale_action.setDisabled(True)
            self.saveXYZAction.setDisabled(True)
            self.save_png_action.setDisabled(True)
            self.undoAction.setDisabled(True)
            self.redoAction.setDisabled(True)
            self.change_image1_action.setDisabled(True)
            self.change_image2_action.setDisabled(True)
            self.change_image3_action.setDisabled(True)
            self.change_image4_action.setDisabled(True)

        else:
            active_window = self.results_windows[self.active_result_window]
            if isinstance(active_window, ResultWindow):
                self.save_png_action.setDisabled(False)
            if isinstance(active_window, TopographyWindow):
                self.scale_action.setDisabled(False)
                self.rotate_clockwise_action.setDisabled(False)
                self.rotate_anticlockwise_action.setDisabled(False)
                self.mirror_ud_action.setDisabled(False)
                self.mirror_lr_action.setDisabled(False)
                self.levelAction.setDisabled(False)
                self.level_planeAction.setDisabled(False)
                self.setZeroLevelAction.setDisabled(False)
                self.filterAction.setDisabled(False)
                self.profileAction.setDisabled(False)
                self.histAction.setDisabled(False)
                self.fft_action.setDisabled(False)
                self.saveXYZAction.setDisabled(False)
                self.change_image_group.actions()[active_window.data.active_ax].setChecked(True)
                for button, av in zip(self.change_image_group.actions(), active_window.data.available_axes):
                    if av:
                        button.setDisabled(False)
            if isinstance(active_window, SpectroscopyWindow):
                self.scale_action.setDisabled(True)
                self.rotate_clockwise_action.setDisabled(True)
                self.rotate_anticlockwise_action.setDisabled(True)
                self.mirror_ud_action.setDisabled(True)
                self.mirror_lr_action.setDisabled(True)
                self.levelAction.setDisabled(True)
                self.level_planeAction.setDisabled(True)
                self.setZeroLevelAction.setDisabled(True)
                self.filterAction.setDisabled(True)
                self.profileAction.setDisabled(True)
                self.histAction.setDisabled(True)
                self.fft_action.setDisabled(True)
                self.saveXYZAction.setDisabled(True)
                self.change_image1_action.setDisabled(True)
                self.change_image2_action.setDisabled(True)
                self.change_image3_action.setDisabled(True)
                self.change_image4_action.setDisabled(True)
            if active_window.winState.undoPossible():
                self.undoAction.setDisabled(False)
            else:
                self.undoAction.setDisabled(True)
            if active_window.winState.redoPossible():
                self.redoAction.setDisabled(False)
            else:
                self.redoAction.setDisabled(True)

    def update_windows(self):
        if self.active_result_window == None:
            self.filterWin.disable()
            self.profileWin.disable()
            self.profileWin.clear_plot()
            self.hist_win.disable()
            self.hist_win.clear_plot()
            self.fft_win.disable()
            self.fft_win.clear_plot()
            self.scale_win.disable()


        else:
            active_window = self.results_windows[self.active_result_window]
            if isinstance(active_window, ResultWindow):
                self.scale_win.enable()
                self.scale_win.update()
            if isinstance(active_window, TopographyWindow):
                self.filterWin.enable()
                self.profileWin.enable()
                if self.profile_win_active:
                    self.profileWin.update_plot()
                self.hist_win.enable()
                if self.hist_win_active:
                    self.hist_win.update_plot()
                self.fft_win.enable()
                if self.fft_win_active:
                    self.fft_win.update_img()

            else:
                self.filterWin.disable()
                self.profileWin.disable()
                self.profileWin.clear_plot()
                self.hist_win.disable()
                self.hist_win.clear_plot()
                self.fft_win.disable()
                self.fft_win.clear_plot()
                self.scale_win.disable()

    def openResultWindow(self, data, filetype):
        if filetype == 'Z' or filetype == 'I':
            win = TopographyWindow(data=data, parent=self)
        if filetype == 'I(V)-curve':
            win = SpectroscopyWindow(data=data, parent=self)
        win.show()

    def openFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Open Files", "", "Z Matrix Files (*.Z_mtrx);;\
                                                I Matrix Files (*.I_mtrx);;\
                                                I(V) Matrix Files (*.I*V*_mtrx)",
                                                options=options)
        for file in files:
            try:
                data, filetype = Files.NewFile(file)
                self.openResultWindow(data, filetype)
            except FileNotFoundError as e:
                if e.args[0] == "NoHeader":
                    QtWidgets.QMessageBox.question(self,
                                                   "Error",
                                                   "No header file (\"_0001.mtrx\") found.",
                                                   QtWidgets.QMessageBox.Ok)

    def openXYZFile(self):
        options = QFileDialog.Options()
        files, _ = QFileDialog.getOpenFileNames(self, "Open Files", "", ".xyz Files (*.xyz)",
                                                options=options)
        ret, points, lines, unit = self.getXYZsize()
        if ret == False:
            return
        shape = [points, lines]
        for file in files:
            try:
                data = Files.NewFileXYZ(file, shape, unit)
                self.openResultWindow(data, 'Z')
            except ValueError:
                QtWidgets.QMessageBox.question(self,
                                               "Error",
                                               "Wrong data dimensions.",
                                               QtWidgets.QMessageBox.Ok)

    def saveXYZFile(self):

        file, _ = QFileDialog.getSaveFileName(self)
        self.results_windows[self.active_result_window].data.saveXYZ(file)

    def save_png(self):
        result_win = self.get_active_window()
        screen = QtWidgets.QApplication.primaryScreen()
        img = screen.grabWindow(result_win.winId())
        file, _ = QFileDialog.getSaveFileName(self, caption="Save .png", filter="Images (*.png)")
        img.save(file, 'png')

    def getXYZsize(self):
        dialog = QtWidgets.QInputDialog()
        dialog.setWindowTitle("XYZ size")
        dialog.setLabelText("Insert number of points and lines.")
        dialog.show()
        dialog.findChild(QtWidgets.QLineEdit).hide()
        #inputs = []
        input_points = QtWidgets.QSpinBox()
        input_points.setRange(0, 1024)
        input_points.setValue(0)
        input_points.setSingleStep(1)
        #inputs.append(input_points)
        input_lines = QtWidgets.QSpinBox()
        input_lines.setRange(0, 1024)
        input_lines.setValue(0)
        input_lines.setSingleStep(1)
        input_unit = QtWidgets.QComboBox()
        input_unit.addItems(["m", "mm", "μm", "nm", "Å", "pm"])
        #inputs.append(input_lines)
        dialog.layout().insertWidget(0, input_points)
        dialog.layout().insertWidget(1, input_lines)
        dialog.layout().insertWidget(2, input_unit)

        ret = dialog.exec_() == QtWidgets.QDialog.Accepted
        return ret, input_points.value(), input_lines.value(), input_unit.currentText()

    def export(self):
        if not self.profile_win_active:
            self.export_win.show()
            self.export_win.update()
        else:
            self.export_win.hide()


    def exitFile(self):
        self.profileWin.close()
        self.hist_win.close()
        self.filterWin.close()
        self.fft_win.close()
        self.close()

    def undoEdit(self):
        result = self.results_windows[self.active_result_window]
        result.undo()
        self._update_menu()
        self._update_push_buttons()
        self.update_windows()

    def redoEdit(self):
        result = self.results_windows[self.active_result_window]
        result.redo()
        self._update_menu()
        self._update_push_buttons()
        self.update_windows()

    def scale(self):
        self.scale_win.show()
        self.update_windows()

    def rotate_clockwise(self):
        if self.results_windows != []:
            result = self.results_windows[self.active_result_window]
            result.modifyData(result.data.rotate90, 1)
            self._update_menu()
            self._update_push_buttons()
            self.update_windows()

    def rotate_anticlockwise(self):
        if self.results_windows != []:
            result = self.results_windows[self.active_result_window]
            result.modifyData(result.data.rotate90, -1)
            self._update_menu()
            self._update_push_buttons()
            self.update_windows()

    def mirror_ud(self):
        if self.results_windows != []:
            result = self.results_windows[self.active_result_window]
            result.modifyData(result.data.mirror_ud)
            self._update_menu()
            self._update_push_buttons()
            self.update_windows()

    def mirror_lr(self):
        if self.results_windows != []:
            result = self.results_windows[self.active_result_window]
            result.modifyData(result.data.mirror_lr)
            self._update_menu()
            self._update_push_buttons()
            self.update_windows()

    def levelEdit(self):
        if self.results_windows != []:
            result = self.results_windows[self.active_result_window]
            result.modifyData(result.data.level_linewise)
            self._update_menu()
            self._update_push_buttons()
            self.update_windows()

    def level_planeEdit(self):
        if self.results_windows != []:
            result = self.results_windows[self.active_result_window]
            result.modifyData(result.data.level_plane)
            self._update_menu()
            self._update_push_buttons()
            self.update_windows()

    def setZeroLevelEdit(self):
        result = self.results_windows[self.active_result_window]
        result.modifyData(result.data.set_zero_level)
        self._update_menu()
        self._update_push_buttons()
        self.update_windows()

    def filterEdit(self):
        if not self.filter_win_active:
            self.filterWin.show()
            self.update_windows()
            self.filter_win_active = True
        else:
            self.filterWin.hide()
            self.filter_win_active = False

    def profileEdit(self):
        if not self.profile_win_active:
            self.profileWin.show()
            self.change_mode('profile')
            self.profile_win_active = True
        else:
            self.profileWin.hide()
            self.change_mode(None)
            self.profile_win_active = False
        self.update_windows()

    def hist_edit(self):
        self.hist_win.show()
        self.hist_win_active = True
        self.update_windows()

    def fft_edit(self):
        self.fft_win.show()
        self.fft_win_active = True
        self.update_windows()

    def change_image(self):
        result = self.results_windows[self.active_result_window]
        for enum, button in enumerate(self.change_image_group.actions()):
            if button.isChecked():
                ax=enum
        result.change_image(ax)

    def aboutHelp(self):
        QtWidgets.QMessageBox.question(self,
                                       "About",
                                       "STMpro 0.0.7 pre-alpha",
                                       QtWidgets.QMessageBox.Ok)

    def change_mode(self, mode):
        self.interaction_mode = mode
        self.update_results()

    def update_results(self):
        for result in self.results_windows:
            result.draw()

    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.WindowActivate:
            self.on_window_activated(self)
            return False

        if event.type() == QtCore.QEvent.Close:
            answer = QtWidgets.QMessageBox.question(self,
                                                    "Confirm Exit...",
                                                    "Are you sure you want to exit?\nAll data will be lost.",
                                                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if answer == QtWidgets.QMessageBox.Yes:
                event.accept()
                self.filterWin.close()
                self.profileWin.close()
                self.hist_win.close()
                self.fft_win.close()
                self.scale_win.close()
                for x in range(len(self.results_windows)):
                    self.results_windows[0].close()
                return False
            else:
                event.ignore()
                return True
        return False

    def setActiveWindow(self, window=None, close=False):
        if close is False:
            self.active_result_window = self.results_windows.index(window)
        else:
            self.active_result_window = None
        self._update_menu()
        self._update_push_buttons()
        self.update_windows()

    def get_active_window(self):
        if self.active_result_window is None:
            return None
        else:
            return self.results_windows[self.active_result_window]

    def on_window_activated(self, active_window):
        if active_window:
            if isinstance(active_window, ResultWindow):
                self.setActiveWindow(window=active_window)
                self.update_windows()

    def close_result(self, window):
        self.setActiveWindow(close=True)
        self.results_windows.pop(self.results_windows.index(window))
