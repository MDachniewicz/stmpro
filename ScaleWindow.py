from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow

import ResultWindow
from Topography import Topography


class ScaleWindow(QMainWindow):
    def __init__(self, parent):
        super(ScaleWindow, self).__init__()
        self.parent = parent
        self._setup(self)
        self._createActions()
        self._connectActions()
        self.update()

        self.x_factor = 1
        self.y_factor = 1
        self.z_factor = 1

    def _setup(self, Win):
        Win.setObjectName("Scale image")
        Win.setFixedSize(310, 440)
        Win.setWindowTitle("Scale")
        self.central_widget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout_2 = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout.addLayout(self.layout_2)

        self.layout_buttons = QtWidgets.QHBoxLayout(self.central_widget)
        self.layout.addLayout(self.layout_buttons)
        self.setCentralWidget(self.central_widget)

    def _createActions(self):

        # Create apply button
        self.applyButton = QtWidgets.QPushButton("Apply", self)
        # self.applyButton.setGeometry(QtCore.QRect(60, 330, 81, 41))
        self.layout_buttons.addWidget(self.applyButton)
        self.applyButton.setObjectName("applyButton")

        # Create cancel button
        self.cancelButton = QtWidgets.QPushButton("Cancel", self)
        self.layout_buttons.addWidget(self.cancelButton)
        # self.cancelButton.setGeometry(QtCore.QRect(170, 330, 81, 41))
        self.cancelButton.setObjectName("cancelButton")

    def _connectActions(self):
        self.cancelButton.clicked.connect(self.cancel)
        self.applyButton.clicked.connect(self.apply)

    def _update_xrange(self):
        self.xrange_label = QtWidgets.QLabel(self.central_widget,
                                             text=f'X range = {self.active_window.data.get_x_range()} {self.active_window.data.xunit}')
        self.layout_2.addWidget(self.xrange_label)

        self.xrange_factor = QtWidgets.QDoubleSpinBox(self)
        self.xrange_factor.setDecimals(4)
        self.xrange_factor.setRange(0.01, 1000)
        self.xrange_factor.setValue(self.x_factor)
        self.xrange_factor.setSingleStep(0.0001)
        self.xrange_factor.valueChanged.connect(self.x_factor_changed)
        self.layout_2.addWidget(self.xrange_factor)

        self.new_xrange_label = QtWidgets.QLabel(self.central_widget,
                                                 text=f'New X range = {self.active_window.data.get_x_range() * self.xrange_factor.value()} {self.active_window.data.xunit}')
        self.layout_2.addWidget(self.new_xrange_label)

    def _update_new_xrange(self):
        self.new_xrange_label.setText(f'New X range = {self.active_window.data.get_x_range()*self.xrange_factor.value()} {self.active_window.data.xunit}')

    def _update_yrange(self):
        self.yrange_label = QtWidgets.QLabel(self.central_widget,
                                             text=f'Y range = {self.active_window.data.get_y_range()} {self.active_window.data.xunit}')
        self.layout_2.addWidget(self.yrange_label)

        self.yrange_factor = QtWidgets.QDoubleSpinBox(self)
        self.yrange_factor.setDecimals(4)
        self.yrange_factor.setRange(0.0001, 1000)
        self.yrange_factor.setValue(self.y_factor)
        self.yrange_factor.setSingleStep(0.0001)
        self.yrange_factor.valueChanged.connect(self.y_factor_changed)
        self.layout_2.addWidget(self.yrange_factor)

        self.new_yrange_label = QtWidgets.QLabel(self.central_widget,
                                                 text=f'New Y range = {self.active_window.data.get_y_range() * self.yrange_factor.value()} {self.active_window.data.xunit}')
        self.layout_2.addWidget(self.new_yrange_label)

    def _update_new_yrange(self):
        self.new_yrange_label.setText(f'New Y range = {self.active_window.data.get_y_range()*self.yrange_factor.value()} {self.active_window.data.yunit}')

    def _update_zrange(self,):
        self.zrange_label = QtWidgets.QLabel(self.central_widget,
                                             text=f'Z range = {self.active_window.data.get_z_range()} {self.active_window.data.unit}')
        self.layout_2.addWidget(self.zrange_label)

        self.zrange_factor = QtWidgets.QDoubleSpinBox(self)
        self.zrange_factor.setDecimals(4)
        self.zrange_factor.setRange(0.01, 1000)
        self.zrange_factor.setValue(self.z_factor)
        self.zrange_factor.setSingleStep(0.00001)
        self.zrange_factor.valueChanged.connect(self.z_factor_changed)
        self.layout_2.addWidget(self.zrange_factor)

        self.new_zrange_label = QtWidgets.QLabel(self.central_widget,
                                                 text=f'New Z range = {self.active_window.data.get_z_range() * self.zrange_factor.value()} {self.active_window.data.unit}')
        self.layout_2.addWidget(self.new_zrange_label)

    def _update_new_zrange(self):
        self.new_zrange_label.setText(f'New Z range = {self.active_window.data.get_z_range()*self.zrange_factor.value()} {self.active_window.data.unit}')


    def update(self):
        for i in reversed(range(self.layout_2.count())):
            self.layout_2.itemAt(i).widget().setParent(None)
        if self.parent.active_result_window != None:
            self.active_window = self.parent.results_windows[self.parent.active_result_window]
            if isinstance(self.active_window, ResultWindow.TopographyWindow):
                self._update_xrange()
                self._update_yrange()
                self._update_zrange()
            if isinstance(self.active_window, ResultWindow.SpectroscopyWindow):
                self._update_xrange()
                self._update_yrange()

    def x_factor_changed(self, value):
        self.x_factor=value
        self._update_new_xrange()

    def y_factor_changed(self, value):
        self.y_factor=value
        self._update_new_yrange()

    def z_factor_changed(self, value):
        self.z_factor = value
        self._update_new_zrange()

    def disable(self):
        self.applyButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)

    def apply(self):
        active_window = self.parent.results_windows[self.parent.active_result_window]
        active_window.modifyData(Topography.scale, param=[self.x_factor, self.y_factor, self.z_factor])
        self.parent.update_windows()

    def cancel(self):
        self.hide()

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.scale_win_active = False
        return False
