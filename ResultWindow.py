# -*- coding: utf-8 -*-
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import copy
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore, QtWidgets

matplotlib.use('Qt5Agg')


class ResultWindow(QMainWindow):
    data = None

    class States:
        def __init__(self, data):
            self.states = [data]
            self.activeState = 0

        def redoPossible(self):
            if self.activeState > 0:
                return True
            else:
                return False

        def undoPossible(self):
            if self.activeState < (len(self.states) - 1):
                return True
            else:
                return False

        def saveState(self, data):
            if self.redoPossible():
                self.states[0] = self.states[self.activeState]
                self.activeState = 0
                del self.states[1:]
            data_cpy = copy.deepcopy(data)
            self.states.insert(1, data_cpy)
            # self.activeState

            if len(self.states) > 5:
                self.states.pop(5)
            self.activeState = 0

        def prevState(self):

            if self.undoPossible():
                self.activeState += 1
                return self.states[self.activeState]

        def nextState(self):
            if self.redoPossible():
                self.activeState -= 1
                return self.states[self.activeState]

    def __init__(self, data=None, parent=None, width=5, height=4, dpi=100, name=None):
        self.parent = parent
        self.data = data
        self.winState = self.States(data)
        if parent is not None:
            parent.results_windows.append(self)

        super(ResultWindow, self).__init__()
        self.installEventFilter(self)
        self.setStyleSheet("background-color: white;")

    def undo(self):
        self.data = self.winState.prevState()
        self.draw()

    def redo(self):
        self.data = self.winState.nextState()
        self.draw()

    def modifyData(self, method, param=None):
        self.winState.saveState(self.data)
        if param is None:
            method()
        else:
            method(param)
        self.draw()

    def draw(self):
        pass

    # Event handling
    def eventFilter(self, source, event):
        # Setting active result window if activated
        if event.type() == QtCore.QEvent.WindowActivate:
            self.parent.on_window_activated(self)
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Close:
            self.parent.close_result(self)
        return False


class Profile:
    def __init__(self, parent, first_point, second_point):
        self.parent = parent
        self.first_point = first_point
        self.second_point = second_point
        self.line = matplotlib.lines.Line2D([self.first_point.x, self.second_point.x],
                                            [self.first_point.y, self.second_point.y])

    def draw_profile(self):
        self.first_point.draw_point()
        self.second_point.draw_point()
        self.parent.canvasImg.axes.add_line(self.line)


class Point:
    def __init__(self, parent, x=0, y=0, x_index=None, y_index=None, size=1):
        self.parent = parent
        self.x_index = x_index
        self.y_index = y_index
        self.x = x
        self.y = y
        self.point = matplotlib.patches.Ellipse((x, y), size, size, fc='r', alpha=0.5, edgecolor='r')
        self.point.set_picker(5)

    def draw_point(self):
        self.parent.canvasImg.axes.add_patch(self.point)


class TopographyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=4.1, height=4, dpi=100, name=None):
        super(TopographyWindow, self).__init__(data, parent, width, height, dpi, name)

        self.plotting_area = QtWidgets.QWidget(self)
        self.plotting_area_layout = QtWidgets.QHBoxLayout(self.plotting_area)

        self.canvasImg = FigureCanvasImg(parent=self, width=width, height=height, dpi=dpi)
        self.canvasColorbar = FigureCanvasColorbar(parent=self, width=width, height=height, dpi=dpi)
        self.plotting_area_layout.addWidget(self.canvasImg)
        self.plotting_area_layout.addWidget(self.canvasColorbar)
        self.canvasColorbar.setMinimumWidth(100)
        self.canvasColorbar.setMaximumWidth(100)

        self.setCentralWidget(self.plotting_area)
        xrange = self.data.get_x_range()

        self.point_size = 0.01 * xrange

        self.scale_bar = True

        self.first_point = None
        self.profile_lines = [[] for i in range(4)]

        self.active_ax = self.data.active_ax

        # Setting window name
        if name is None:
            self.setWindowTitle(data.name)
        self.show()
        self.draw()

    def change_image(self, ax):
        self.winState.saveState(self.data)
        self.data.change_ax(ax)
        self.active_ax = ax
        self.draw()

    def draw(self):
        self.setWindowTitle(self.data.name)
        self.canvasImg.axes.cla()
        self.canvasColorbar.axes.cla()
        im = self.canvasImg.axes.pcolormesh(self.data.X, self.data.Y, self.data.Z, cmap='afmhot', picker=True)
        self.canvasColorbar.fig.colorbar(im, cax=self.canvasColorbar.axes)
        self.canvasColorbar.axes.set_title(self.data.unit)
        self.canvasImg.axes.set_aspect('equal')
        if self.parent.interaction_mode == 'profile':
            self._draw_profile_lines()
        else:
            if self.scale_bar:
                self._draw_scale_bar()
        self.canvasImg.draw()
        self.canvasColorbar.draw()

    def _draw_profile_lines(self):
        if self.first_point != None:
            self.first_point.draw_point()
        if self.profile_lines[self.active_ax] != []:
            for x in self.profile_lines[self.active_ax]:
                x.draw_profile()
        self.parent.profileWin.update_plot()

    def _draw_profile(self, profile):
        profile.draw_profile()
        self.canvasImg.draw()
        self.parent.profileWin.update_plot()

    def _draw_point(self, point):
        point.draw_point()
        self.canvasImg.draw()

    def _draw_scale_bar(self):
        shape = self.data.X.shape
        xrange = self.data.get_x_range()
        length = round(0.2 * xrange)
        text = str(length) + ' ' + self.data.xunit
        x1 = self.data.X[1, round(0.1 * shape[0])]
        x2 = self.data.X[1, round(0.3 * shape[0])]
        y1 = self.data.Y[round(0.12 * shape[0]), 1]
        y2 = self.data.Y[round(0.12 * shape[0]), 1]
        line = matplotlib.lines.Line2D([x1, x2],
                                       [y1, y2], linewidth=0.01 * shape[1],
                                       color='black', solid_capstyle='butt')
        text = matplotlib.text.Text(x=self.data.X[1, round(0.2 * shape[0])], y=self.data.Y[round(0.15 * shape[1]), 1],
                                    text=text,
                                    horizontalalignment='center', fontsize=13)
        self.canvasImg.axes.add_line(line)
        self.canvasImg.axes.add_artist(text)

    def mouse_press(self, e, indices):
        if e.inaxes != self.canvasImg.axes:
            return
        if self.parent.interaction_mode == 'profile':
            line = int(indices / self.data.Z.shape[1])
            point = int(indices % (self.data.Z.shape[0]))
            x = self.data.X[line, point]
            y = self.data.Y[line, point]
            if self.first_point == None:
                self.first_point = Point(parent=self, x=x, y=y, x_index=point, y_index=line, size=self.point_size)
                self._draw_point(self.first_point)
            else:
                second_point = Point(parent=self, x=x, y=y, x_index=point, y_index=line, size=self.point_size)
                profile_line = Profile(parent=self, first_point=self.first_point, second_point=second_point)
                self.profile_lines[self.active_ax].append(profile_line)
                self.first_point = None
                self._draw_profile(profile_line)

    def mouse_press_right(self, e, artist=None):
        if e.inaxes != self.canvasImg.axes:
            return
        if artist == None:
            if self.first_point != None:
                self.first_point = None
            else:
                return
        else:
            for enum, profile in enumerate(self.profile_lines[self.active_ax]):
                if profile.first_point.point == artist or profile.second_point.point == artist:
                    self.profile_lines[self.active_ax].pop(enum)
        self.draw()



class SpectroscopyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=4.5, height=4, dpi=100, name=None):
        super().__init__(None, parent, width, height, dpi, name)
        self.data = data

        self.forward = True
        if self.data.ramp_reversal:
            self.backward = True
        else:
            self.backward = False

        self.canvas = FigureCanvas(self)
        self._setup_ui()

        self.show()
        self.draw()

    def _setup_ui(self):
        self.central_widget = QtWidgets.QWidget(self)
        self.layout_main = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout_main.addWidget(self.canvas)
        self.layout_controls = QtWidgets.QVBoxLayout(self.central_widget)

        self.setting_forward = QtWidgets.QCheckBox('Forward', self)
        self.setting_forward.setChecked(self.forward)
        self.setting_forward.toggled.connect(self._setting_forward_changed)
        self.layout_controls.addWidget(self.setting_forward)

        self.setting_backward = QtWidgets.QCheckBox('Backward', self)
        self.setting_backward.setChecked(self.backward)
        self.setting_backward.toggled.connect(self._setting_backward_changed)
        self.layout_controls.addWidget(self.setting_backward)

        self.layout_main.addLayout(self.layout_controls)
        self.setCentralWidget(self.central_widget)

    def _setting_forward_changed(self, value):
        self.forward = self.setting_forward.isChecked()
        self.draw()

    def _setting_backward_changed(self, value):
        self.backward = self.setting_backward.isChecked()
        self.draw()

    def draw(self):
        self.canvas.axes.cla()
        self.canvas.axes.grid(True)
        if self.forward:
            self.canvas.axes.plot(self.data.x, self.data.y_forward, color='blue')
        if self.backward:
            self.canvas.axes.plot(self.data.x, self.data.y_backward, color='red')
        self.canvas.axes.set_xlabel(self.data.xunit)
        self.canvas.axes.set_ylabel(self.data.unit)
        self.canvas.fig.tight_layout(pad=0.1)
        self.canvas.draw()


class SpectroscopyMapWindow(ResultWindow):
    def __init__(self, data, parent=None, width=4.5, height=4, dpi=100, name=None):
        super(SpectroscopyMapWindow, self).__init__(data, parent, width, height, dpi, name)
        self.data = data
        self.im = None
        self.active_plane = 0

        self._setup_ui()
        self.show()
        self.draw()

    def _setup_ui(self):
        self.central_widget = QtWidgets.QWidget(self)
        self.layout_main = QtWidgets.QVBoxLayout(self.central_widget)

        self.layout_results = QtWidgets.QHBoxLayout(self.central_widget)
        self.canvas_map = FigureCanvasImg(self)
        self.canvas_colorbar = FigureCanvasColorbar(self)
        self.canvas_colorbar.setMinimumWidth(100)
        self.canvas_colorbar.setMaximumWidth(100)
        self.canvas_plot = FigureCanvas(self)
        self.layout_results.addWidget(self.canvas_map)
        self.layout_results.addWidget(self.canvas_colorbar)
        self.layout_results.addWidget(self.canvas_plot)
        self.layout_main.addLayout(self.layout_results)

        self.layout_controls = QtWidgets.QHBoxLayout(self.central_widget)
        self.setting_plane = QtWidgets.QSpinBox(self.central_widget)
        self.setting_plane.setRange(0, len(self.data.planes)-1)
        self.setting_plane.setValue(self.active_plane)
        self.setting_plane.valueChanged.connect(self._active_plane_changed)
        self.layout_controls.addWidget(self.setting_plane)
        self.layout_main.addLayout(self.layout_controls)

        self.setCentralWidget(self.central_widget)


        # First time drawing image and colorbar. Then draw() only updates colorbar instead of redrawing it. Significant performace difference.
        self.im = self.canvas_map.axes.pcolormesh(self.data.x, self.data.y, self.data.z_forward[:, :, self.active_plane],
                                             cmap='afmhot', picker=True)
        self.cb = self.canvas_colorbar.fig.colorbar(self.im, cax=self.canvas_colorbar.axes)
        self.canvas_colorbar.axes.set_title(self.data.unit)

    def _active_plane_changed(self, value):
        self.active_plane = value
        self.draw()

    def draw(self):
        self.canvas_map.axes.cla()
        self.im = self.canvas_map.axes.pcolormesh(self.data.x, self.data.y, self.data.z_forward[:, :, self.active_plane], cmap='afmhot', picker=True)
        self.cb.update_normal(self.im)
        self.canvas_colorbar.axes.set_title(self.data.unit)
        self.canvas_map.axes.set_aspect('equal')
        self.canvas_map.draw()
        self.canvas_colorbar.draw()



    def mouse_press(self, e, indices):
        if e.inaxes != self.canvas_map:
            return
        if self.parent.interaction_mode == 'curve_picking':
            line = int(indices / self.data.Z.shape[1])
            point = int(indices % (self.data.Z.shape[0]))
            x = self.data.X[line, point]
            y = self.data.Y[line, point]
            if self.first_point == None:
                self.first_point = Point(parent=self, x=x, y=y, x_index=point, y_index=line, size=self.point_size)
                self._draw_point(self.first_point)
            else:
                second_point = Point(parent=self, x=x, y=y, x_index=point, y_index=line, size=self.point_size)
                profile_line = Profile(parent=self, first_point=self.first_point, second_point=second_point)
                self.profile_lines[self.active_ax].append(profile_line)
                self.first_point = None
                self._draw_profile(profile_line)

    def mouse_press_right(self, e, artist=None):
        if e.inaxes != self.canvasImg.axes:
            return
        if artist == None:
            if self.first_point != None:
                self.first_point = None
            else:
                return
        else:
            for enum, profile in enumerate(self.profile_lines[self.active_ax]):
                if profile.first_point.point == artist or profile.second_point.point == artist:
                    self.profile_lines[self.active_ax].pop(enum)
        self.draw()

class SingleCurve():
    def __init__(self, parent, x=0, y=0, x_index=None, y_index=None, size=1):
        self.parent = parent
        self.x_index = x_index
        self.y_index = y_index
        self.x = x
        self.y = y
        self.point = matplotlib.patches.Ellipse((x, y), size, size, fc='r', alpha=0.5, edgecolor='r')
        self.point.set_picker(5)

    def draw_point(self):
        self.parent.canvasImg.axes.add_patch(self.point)

class AreaCurves:
    def __init__(self, parent, x=0, y=0, x_index=None, y_index=None, size=1):
        self.parent = parent
        self.x_index = x_index
        self.y_index = y_index
        self.x = x
        self.y = y
        self.point = matplotlib.patches.Ellipse((x, y), size, size, fc='r', alpha=0.5, edgecolor='r')
        self.point.set_picker(5)

    def draw_point(self):
        self.parent.canvasImg.axes.add_patch(self.point)

class ProfileResultWindow(ResultWindow):
    def __init__(self, profile=None, parent=None, width=4.5, height=4, dpi=100, name=None):
        super().__init__(None, parent, width, height, dpi, name)
        self.canvas = FigureCanvas(self)
        self.setCentralWidget(self.canvas)
        self.profile = profile
        if name is not None:
            self.setWindowTitle(name)
        else:
            self.setWindowTitle('Profiles')

        self.unit, self.xunit = self.get_unit()
        self.set_profile_units()
        self.show()
        self.draw()

    def draw(self):

        self.canvas.axes.cla()
        for enum, prof in enumerate(self.profile):
            self.canvas.axes.plot(prof.distance, prof.profile)

        self.canvas.axes.set_xlabel(self.xunit)
        self.canvas.axes.set_ylabel(self.unit)
        self.canvas.draw()

    # Looking for profiles with maximum ranges to set units in output graph
    def get_unit(self):
        max_xrange = self.profile[0].get_xrange()
        max_xrange_index = 0
        max_range = self.profile[0].get_range()
        max_range_index = 0
        for enum, prof in enumerate(self.profile):
            if prof.get_xrange() > max_xrange:
                max_xrange_index = enum
                max_xrange = prof.get_xrange()
            if prof.get_xrange() > max_range:
                max_range_index = enum
                max_range = prof.get_range()
        # Set automatic units on profiles with largest ranges
        self.profile[max_xrange_index].auto_units()
        self.profile[max_range_index].auto_units()
        # Set x-axis and y-axis units
        xunit = self.profile[max_xrange_index].xunit
        unit = self.profile[max_range_index].unit
        return unit, xunit

    def auto_profile_units(self):
        for prof in self.profile:
            prof.auto_units()

    def set_profile_units(self):
        for prof in self.profile:
            prof.set_profile_units(self.xunit, self.unit)


class HistogramResultWindow(ResultWindow):
    def __init__(self, bins=None, histogram=None, parent=None, width=4.5, height=4, dpi=100, name=None):
        super().__init__(None, parent, width, height, dpi, name)
        self.canvas = FigureCanvas(self)
        self.setCentralWidget(self.canvas)
        self.bins = bins
        self.histogram = histogram
        if name is not None:
            self.setWindowTitle(name)
        else:
            self.setWindowTitle('Histogram')
        self.show()
        self.draw()

    def draw(self):
        self.canvas.axes.cla()
        self.canvas.axes.stairs(self.histogram, self.bins, fill=True)
        self.canvas.draw()


class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(FigureCanvas, self).__init__(fig)


class FigureCanvasColorbar(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_position([0.15, 0.02, 0.2, 0.87])
        self.axes.tick_params(labelsize=8)
        self.axes.yaxis.get_offset_text().set_fontsize(8)

        super(FigureCanvasColorbar, self).__init__(self.fig)


class FigureCanvasImg(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_axis_off()
        self.axes.get_xaxis().set_visible(False)
        self.axes.get_yaxis().set_visible(False)
        self.axes.set_position([0.01, 0.01, 0.98, 0.98])
        self.parent = parent
        self.indices = [0, 0]
        self.artist = None
        self.button = None
        super(FigureCanvasImg, self).__init__(self.fig)
        self.connect()

    def connect(self):
        self.cidpress = self.mpl_connect(
            'button_press_event', self.on_press)
        self.cidrelease = self.mpl_connect(
            'button_release_event', self.on_release)
        self.cidmove = self.mpl_connect(
            'motion_notify_event', self.on_move)
        self.cidpick = self.mpl_connect(
            'pick_event', self.on_pick)

    def on_press(self, e):
        if isinstance(e, matplotlib.backend_bases.PickEvent):
            artist = e.artist
        if isinstance(e, matplotlib.backend_bases.MouseEvent):
            if e.button == 1:
                self.button = 'left'
            if e.button == 3:
                self.button = 'right'

    def on_release(self, e):
        if self.artist == None and self.button == 'left':
            self.parent.mouse_press(e, self.indices)
        if self.artist == None and self.button == 'right':
            self.parent.mouse_press_right(e)
        if self.artist != None and self.button == 'right':
            self.parent.mouse_press_right(e, self.artist)
        self.button = None
        self.artist = None

    def on_move(self, e):
        pass

    def on_pick(self, e):
        if isinstance(e.artist, matplotlib.patches.Ellipse):
            self.artist = e.artist
        if isinstance(e.artist, matplotlib.collections.QuadMesh):
            self.indices = e.ind
