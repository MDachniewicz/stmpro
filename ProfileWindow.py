from PyQt5.QtWidgets import QDialog, QSlider, QLabel, QWidget, QMainWindow
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ProfileWindow(QDialog):
    def __init__(self, parent):
        super(ProfileWindow, self).__init__()
        self.parent = parent
        self._setup()
        self._createActions()
        self._connectActions()

        self.installEventFilter(self)
        self.profile_width = 3
        self._update()

    def _setup(self):
        self.setObjectName("Profile Window")
        self.setFixedSize(750, 440)
        self.setWindowTitle("Profile")

        self.plotting_area = QtWidgets.QWidget(self)
        self.plotting_area.setGeometry(QtCore.QRect(20, 20, 700, 300))

        self.plotting_area_layout = QtWidgets.QVBoxLayout(self.plotting_area)
        self.canvas = FigureCanvas(self, 5, 3, 100)
        self.plotting_area_layout.addWidget(self.canvas)
        self.update_plot()

    def update_plot(self):
        self.canvas.axes.cla()
        if self.parent.active_result_window != None:
            active_window = self.parent.resultsWindows[self.parent.active_result_window]
            for profile in active_window.profile_lines:
                x1 = round(profile.first_point.x)
                x2 = round(profile.second_point.x)
                y1 = round(profile.first_point.y)
                y2 = round(profile.second_point.y)
                distance, profile=active_window.data.get_profile((x1,y1), (x2, y2), self.profile_width)
                self.canvas.axes.plot(distance, profile)
                self.canvas.draw()

    def _createActions(self):
        self.slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(QtCore.QRect(20, 350, 150, 20))
        self.slider.setRange(1, 40)
        self.slider.setValue(3)
        self.slider.setSingleStep(1)

        self.profile_width_display = QLabel(f'Profile Width: {3}', self)
        self.profile_width_display.setGeometry(QtCore.QRect(180, 350, 80, 20))

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
        self.slider.valueChanged.connect(self._update_profile_width)

    def _update(self):
        pass

    def _update_profile_width(self, value):
        self.profile_width = value
        self.profile_width_display.setText(f'Profile Width: {value}')

    def disable(self):
        self.applyButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)

    def apply(self):
        pass

    def cancel(self):
        self.hide()

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.interaction_mode = None
        return False


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)
