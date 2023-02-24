from PyQt5.QtWidgets import QDialog, QSlider, QLabel, QWidget, QMainWindow
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ResultWindow import HistogramResultWindow

class HistogramWindow(QDialog):
    def __init__(self, parent):
        super(HistogramWindow, self).__init__()
        self.parent = parent
        self._setup()
        self._createActions()
        self._connectActions()

        self.installEventFilter(self)
        self.n_bins = 40

    def _setup(self):
        self.setObjectName("Histogram Window")
        self.setFixedSize(750, 440)
        self.setWindowTitle("Histogram")

        self.plotting_area = QtWidgets.QWidget(self)
        self.plotting_area.setGeometry(QtCore.QRect(20, 20, 700, 300))

        self.plotting_area_layout = QtWidgets.QVBoxLayout(self.plotting_area)
        self.canvas = FigureCanvas(self, 5, 3, 100)
        self.plotting_area_layout.addWidget(self.canvas)
        self.update_plot()

    def update_plot(self):
        self.canvas.axes.cla()
        if self.parent.active_result_window is not None:
            active_window = self.parent.results_windows[self.parent.active_result_window]
            hist, bins = active_window.data.histogram(self.n_bins)
            self.canvas.axes.stairs(hist, bins)
            self.canvas.draw()

    def clear_plot(self):
        self.canvas.axes.cla()
        self.canvas.draw()

    def _createActions(self):
        self.spin_box = QtWidgets.QSpinBox(self)
        self.spin_box.setGeometry(QtCore.QRect(20, 350, 150, 20))
        self.spin_box.setRange(1, 1024)
        self.spin_box.setValue(40)
        self.spin_box.setSingleStep(1)

        # Create apply button
        self.applyButton = QtWidgets.QPushButton("Apply", self)
        self.applyButton.setGeometry(QtCore.QRect(520, 350, 70, 30))
        self.applyButton.setObjectName("applyButton")

        # Create cancel button
        self.cancelButton = QtWidgets.QPushButton("Cancel", self)
        self.cancelButton.setGeometry(QtCore.QRect(630, 350, 70, 30))
        self.cancelButton.setObjectName("cancelButton")

    def _connectActions(self):
        self.applyButton.clicked.connect(self.apply)
        self.cancelButton.clicked.connect(self.cancel)
        self.spin_box.valueChanged.connect(self._update_n_bins)

    def _update_n_bins(self, value):
        self.n_bins = value
        self.update_plot()

    def disable(self):
        self.applyButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)

    def apply(self):
        active_window = self.parent.results_windows[self.parent.active_result_window]
        hist, bins = active_window.data.histogram(self.n_bins)
        histogram_win = HistogramResultWindow(bins=bins, histogram=hist, parent=self.parent)
        #self.parent.results_windows.append(histogram_win)

    def cancel(self):
        self.hide()

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.hist_win_active = False
        return False

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)
