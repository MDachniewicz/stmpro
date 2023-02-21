# -*- coding: utf-8 -*-
"""
Created on Thu Jan 26 22:17:12 2023

@author: marek
"""
import matplotlib

matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import copy
from PyQt5.QtWidgets import QMainWindow
from PyQt5 import QtCore, QtWidgets


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

        super(ResultWindow, self).__init__()
        self.installEventFilter(self)
        # Creating figure canvas
        #self.canvas = FigureCanvasColorbar(parent=self, width=width, height=height, dpi=dpi)
        #self.setCentralWidget(self.canvas)

        # Setting windown name
        if name == None:
            self.setWindowTitle(data.filename)
    '''
    # Ploting image in axes        
    def drawPlot(self):

        self.canvas.axesImg.cla()
        self.canvas.axesColorbar.cla()
        im = self.canvas.axesImg.pcolormesh(self.data.X * 10 ** 9, self.data.Y * 10 ** 9, self.data.Z * 10 ** 9)
        self.canvas.fig.colorbar(im, cax=self.canvas.axesColorbar)
        self.canvas.axesImg.set_aspect('equal')
        if self.first_point != None:
            self.first_point.draw_point()
        if self.profile_lines != []:
            for x in self.profile_lines:
                x.draw_profile()
        self.canvas.draw()
    '''
    def undo(self):
        self.data = self.winState.prevState()
        self.drawPlot()

    def redo(self):
        self.data = self.winState.nextState()
        self.drawPlot()

    def modifyData(self, method, param=None):
        self.winState.saveState(self.data)
        if param == None:
            method()
        else:
            method(param)
        self.drawPlot()

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
        self.parent=parent
        self.first_point=first_point
        self.second_point=second_point
        self.line=matplotlib.lines.Line2D([self.first_point.x, self.second_point.x],[self.first_point.y, self.second_point.y] )

    def draw_profile(self):
        self.first_point.draw_point()
        self.second_point.draw_point()
        self.parent.canvasImg.axes.add_line(self.line)


class Point:
    def __init__(self, parent, x=0, y=0, size=1):
        self.parent = parent
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
        self.point_size = 5

        self.first_point = None
        self.profile_lines = []
        self.show()
        self.drawPlot()



    def drawPlot(self):
        self.canvasImg.axes.cla()
        self.canvasColorbar.axes.cla()
        im = self.canvasImg.axes.pcolormesh(self.data.Z * 10 ** 9)
        self.canvasColorbar.fig.colorbar(im, cax=self.canvasColorbar.axes)
        self.canvasColorbar.axes.set_title(self.data.unit)
        self.canvasImg.axes.set_aspect('equal')
        self._draw_profile_lines()
        self.canvasImg.draw()
        self.canvasColorbar.draw()

    def _draw_profile_lines(self):
        if self.first_point != None:
            self.first_point.draw_point()
        if self.profile_lines != []:
            for x in self.profile_lines:
                x.draw_profile()
        self.parent.profileWin.update_plot()

    def mouse_press(self, e):
        if e.inaxes != self.canvasImg.axes:
            return
        if self.parent.interaction_mode == 'profile':

            if self.first_point == None:
                self.first_point = Point(parent=self, x=e.xdata, y=e.ydata, size=self.point_size)
                self.drawPlot()
            else:
                second_point = Point(parent=self, x=e.xdata, y=e.ydata, size=self.point_size)
                profile_line = Profile(parent=self, first_point=self.first_point, second_point=second_point)
                self.profile_lines.append(profile_line)
                self.first_point = None
                self.drawPlot()

    def mouse_press_right(self, e, artist):
        if e.inaxes != self.canvasImg.axes:
            return
        if artist == None:
            return
        if self.first_point != None:
            self.first_point=None
        else:
            for enum, profile in enumerate(self.profile_lines):
                if profile.first_point.point == artist or profile.second_point.point == artist:
                    self.profile_lines.pop(enum)
        self.drawPlot()

    def mouse_release(self, e):
        pass

    def mouse_move(self, e):
        pass

class SpectroscopyWindow(ResultWindow):
    def __init__(self, data=None, parent=None, width=4.5, height=4, dpi=100, name=None):
        super().__init__(data, parent, width, height, dpi, name)
        self.canvas=FigureCanvas(self)
        self.setCentralWidget(self.canvas)
        self.show()
        self.drawPlot()

    def drawPlot(self):
        self.canvas.axes.cla()
        self.canvas.axes.plot(self.data.V, self.data.currentForw)
        self.canvas.draw()

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(FigureCanvas, self).__init__(self.fig)

class FigureCanvasColorbar(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        self.axes.set_position([0.2, 0.05, 0.2, 0.9])
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
            artist=e.artist
        if isinstance(e, matplotlib.backend_bases.MouseEvent):
            if e.button == 1:
                self.button = 'left'
            if e.button == 3:
                self.button = 'right'

    def on_release(self, e):
        if self.artist == None and self.button == 'left':
            self.parent.mouse_press(e)
        if self.artist != None and self.button =='right':
            self.parent.mouse_press_right(e, self.artist)
        self.button = None
        self.artist = None


    def on_move(self, e):
        self.parent.mouse_move(e)

    def on_pick(self, e):
        if isinstance(e.artist, matplotlib.patches.Ellipse):
            self.artist=e.artist


