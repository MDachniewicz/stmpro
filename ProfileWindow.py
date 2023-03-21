from PyQt5.QtWidgets import QDialog, QSlider, QLabel, QWidget, QMainWindow
from PyQt5 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import ResultWindow
from Topography import ProfileData


class ProfileWindow(QDialog):
    def __init__(self, parent):
        super(ProfileWindow, self).__init__()
        self.parent = parent
        self._setup()
        self._createActions()
        self._connectActions()

        self.installEventFilter(self)
        self.profile_width = 3

        # If profiles should be opened in separate windows
        self.separate_profiles = False

    def _setup(self):
        self.setObjectName("Profile Window")
        self.setFixedSize(750, 440)
        self.setWindowTitle("Profile")

        self.plotting_area = QtWidgets.QWidget(self)
        self.plotting_area.setGeometry(QtCore.QRect(0, 0, 750, 320))

        self.plotting_area_layout = QtWidgets.QVBoxLayout(self.plotting_area)
        self.canvas = FigureCanvas(self, 5, 3, 100)
        self.plotting_area_layout.addWidget(self.canvas)
        self.update_plot()

    def update_plot(self):
        self.canvas.axes.cla()
        if self.parent.active_result_window != None:
            active_window = self.parent.results_windows[self.parent.active_result_window]
            active_ax = active_window.active_ax
            for profile in active_window.profile_lines[active_ax]:
                x1 = profile.first_point.x_index
                x2 = profile.second_point.x_index
                y1 = profile.first_point.y_index
                y2 = profile.second_point.y_index
                if isinstance(active_window, ResultWindow.TopographyWindow):
                    distance, profile = active_window.data.get_profile((x1, y1), (x2, y2), self.profile_width)
                else:
                    distance, profile = active_window.data[1].get_profile((x1, y1), (x2, y2), self.profile_width)
                self.canvas.axes.plot(distance, profile)
            if isinstance(active_window, ResultWindow.TopographyWindow):
                self.canvas.axes.set_ylabel(active_window.data.unit)
                self.canvas.axes.set_xlabel(active_window.data.xunit)
            else:
                self.canvas.axes.set_ylabel(active_window.data[1].unit)
                self.canvas.axes.set_xlabel(active_window.data[1].xunit)
            self.canvas.draw()

    def clear_plot(self):
        self.canvas.axes.cla()
        self.canvas.draw()

    def _createActions(self):
        self.slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(QtCore.QRect(20, 350, 150, 20))
        self.slider.setRange(1, 40)
        self.slider.setValue(3)
        self.slider.setSingleStep(1)

        self.profile_width_display = QLabel(f'Profile Width: {3}', self)
        self.profile_width_display.setGeometry(QtCore.QRect(180, 350, 80, 20))

        # Create check box
        self.checkbox = QtWidgets.QCheckBox(parent=self, text='Separate profiles')
        self.checkbox.setGeometry(QtCore.QRect(20, 390, 150, 20))

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
        self.slider.valueChanged.connect(self._update_profile_width)
        self.checkbox.toggled.connect(self._update_separate_windows)
        self.checkbox.setChecked(False)

    def _update_profile_width(self, value):
        self.profile_width = value
        self.profile_width_display.setText(f'Profile Width: {value}')
        self.update_plot()

    def _update_separate_windows(self):
        if self.checkbox.isChecked():
            self.separate_profiles = True
        else:
            self.separate_profiles = False

    def disable(self):
        self.applyButton.setDisabled(True)
        self.clearButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)
        self.clearButton.setDisabled(False)

    def apply(self):
        active_window = self.parent.results_windows[self.parent.active_result_window]
        if isinstance(active_window, ResultWindow.TopographyWindow):
            unit, xunit, _ = active_window.data.get_units()
        else:
            unit, xunit, _ = active_window.data[1].get_units()
        active_ax = active_window.active_ax
        if self.separate_profiles:
            for enum, profile in enumerate(active_window.profile_lines[active_ax]):
                x1 = profile.first_point.x_index
                x2 = profile.second_point.x_index
                y1 = profile.first_point.y_index
                y2 = profile.second_point.y_index
                if isinstance(active_window, ResultWindow.TopographyWindow):
                    distance, profile = active_window.data.get_profile((x1, y1), (x2, y2), self.profile_width)
                else:
                    distance, profile = active_window.data[1].get_profile((x1, y1), (x2, y2), self.profile_width)
                name = 'Profile' + str(enum)
                profile = [ProfileData(distance, profile, unit=unit, xunit=xunit, name=name)]
                ResultWindow.ProfileResultWindow(profile=profile, parent=self.parent, name=name)
        else:
            profiles = []

            for enum, profile in enumerate(active_window.profile_lines[active_ax]):
                x1 = profile.first_point.x_index
                x2 = profile.second_point.x_index
                y1 = profile.first_point.y_index
                y2 = profile.second_point.y_index
                if isinstance(active_window, ResultWindow.TopographyWindow):
                    distance, profile = active_window.data.get_profile((x1, y1), (x2, y2), self.profile_width)
                else:
                    distance, profile = active_window.data[1].get_profile((x1, y1), (x2, y2), self.profile_width)
                name = 'Profile' + str(enum)
                profiles.append(ProfileData(distance, profile, unit=unit, xunit=xunit, name=name))
            name = 'Profiles'
            ResultWindow.ProfileResultWindow(profile=profiles, parent=self.parent, name=name)

    def cancel(self):
        self.hide()

    def clear(self):
        if self.parent.active_result_window is not None:
            active_window = self.parent.results_windows[self.parent.active_result_window]
            active_window.profile_lines = [[] for i in range(4)]
            active_window.first_point = None
            active_window.draw()
            self.clear_plot()

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.change_mode(None)
            self.parent.profile_win_active = False
            self.parent.profile_button.setChecked(False)
        return False


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_position([0.1, 0.2, 0.85, 0.78])
        super(FigureCanvas, self).__init__(fig)
