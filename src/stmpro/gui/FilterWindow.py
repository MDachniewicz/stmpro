# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 14:20:08 2023

@author: marek
"""

from PyQt5.QtWidgets import QDialog, QComboBox, QSlider, QLabel
from PyQt5 import QtCore, QtWidgets
from src.stmpro.data.Topography import Topography


class FilterWindow(QDialog):
    filters = ["Median", "Mean"]
    maskSize = 3

    def __init__(self, parent):
        super(FilterWindow, self).__init__()
        self.parent = parent
        self._setup(self)
        self._createActions()
        self._connectActions()
        self.installEventFilter(self)
        self.active_filter = 0
        self._update()

    def _setup(self, Win):
        Win.setObjectName("Filter image")
        Win.setFixedSize(310, 440)
        Win.setWindowTitle("Filter")

    def _createActions(self):
        # Create list of filters
        self.filterList = QComboBox(self)
        self.filterList.addItems(self.filters)
        self.filterList.setGeometry(QtCore.QRect(10, 20, 80, 20))

        # Create apply button
        self.applyButton = QtWidgets.QPushButton("Apply", self)
        self.applyButton.setGeometry(QtCore.QRect(60, 330, 81, 41))
        self.applyButton.setObjectName("applyButton")

        # Create cancel button
        self.cancelButton = QtWidgets.QPushButton("Cancel", self)
        self.cancelButton.setGeometry(QtCore.QRect(170, 330, 81, 41))
        self.cancelButton.setObjectName("cancelButton")

    def _connectActions(self):
        self.applyButton.clicked.connect(self.apply)
        self.cancelButton.clicked.connect(self.cancel)

        self.filterList.currentIndexChanged.connect(self.index_changed)

    def _update(self):
        self.inputs = []
        if self.active_filter in [0, 1]:
            slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
            slider.setGeometry(QtCore.QRect(20, 100, 150, 20))
            slider.setRange(1, 20)
            slider.setValue(3)
            slider.setSingleStep(1)
            slider.valueChanged.connect(self.updateMaskSize)
            self.inputs.append(slider)
            result_label = QLabel(f'Mask Size: {3}', self)
            result_label.setGeometry(QtCore.QRect(180, 100, 80, 20))
            self.inputs.append(result_label)

    def updateMaskSize(self, value):
        self.maskSize = value
        self.inputs[1].setText(f'Mask Size: {value}')

    def disable(self):
        self.applyButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)

    def apply(self):
        active_window = self.parent.results_windows[self.parent.active_result_window]
        if self.filters[self.active_filter] == "Median":
            active_window.modifyData(Topography.median, param=self.maskSize)
        if self.filters[self.active_filter] == "Mean":
            active_window.modifyData(Topography.mean, param=self.maskSize)
        self.parent.update_windows()

    def cancel(self):
        self.hide()


    def index_changed(self, i):
        self.active_filter = i
        self._update()

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.filter_win_active = False
            self.parent.filter_button.setChecked(False)
        return False
