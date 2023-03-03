from PyQt5.QtWidgets import QDialog, QSlider, QLabel, QWidget, QMainWindow
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from ResultWindow import TopographyWindow
from Images import fft_image


class FourierWindow(QDialog):
    def __init__(self, parent):
        super(FourierWindow, self).__init__()
        self.parent = parent
        self._setup()
        self._createActions()
        self._connectActions()
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.installEventFilter(self)
        self.profile_width = 3

        # If profiles should be opened in separate windows
        self.separate_profiles = False

    def _setup(self):
        self.setObjectName("Fourier Window")
        self.setFixedSize(750, 440)
        self.setWindowTitle("FFT")

        self.plotting_area = QtWidgets.QWidget(self)
        self.plotting_area.setGeometry(QtCore.QRect(0, 0, 750, 320))

        self.plotting_area_layout = QtWidgets.QHBoxLayout(self.plotting_area)

        self.canvas_img = FigureCanvas(self, 5, 5, 100)
        self.canvas_fft = FigureCanvas(self, 5, 5, 100)
        self.plotting_area_layout.addWidget(self.canvas_fft)
        self.plotting_area_layout.addWidget(self.canvas_img)
        self.update_img()

    def update_img(self):
        self.canvas_img.axes.cla()
        if self.parent.active_result_window != None:
            active_window = self.parent.results_windows[self.parent.active_result_window]
            if isinstance(active_window, TopographyWindow):
                fft_image=active_window.data.fft()
                ifft_image=active_window.data.ifft(fft_image)
                self.canvas_img.axes.pcolormesh(active_window.data.X, active_window.data.Y, ifft_image, cmap='afmhot')
                self.canvas_img.draw()
                self.canvas_img.axes.set_aspect('equal')
                self.canvas_fft.axes.pcolormesh(abs(fft_image))
                self.canvas_fft.draw()
                self.canvas_fft.axes.set_aspect('equal')

    def clear_plot(self):
        self.canvas_img.axes.cla()
        self.canvas_img.draw()

    def _createActions(self):
        # Create clear button
        self.clearButton = QtWidgets.QPushButton("Clear", self)
        self.clearButton.setGeometry(QtCore.QRect(410, 350, 70, 30))
        self.clearButton.setObjectName("clearButton")

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
        self.clearButton.clicked.connect(self.clear)

    def disable(self):
        self.applyButton.setDisabled(True)
        self.clearButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)
        self.clearButton.setDisabled(False)

    def apply(self):
        pass

    def cancel(self):
        self.hide()

    def clear(self):
        pass

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.fft_win_active = False
        return False


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_axis_off()
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.axes.set_position([0.01, 0.01, 0.98, 0.98])
        super(FigureCanvas, self).__init__(fig)


