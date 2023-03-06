from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QComboBox, QCheckBox, QSpinBox, QFileDialog

import ResultWindow
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ExportWindow(QMainWindow):
    FILETYPES_TOPO = ['png', 'jpg']
    def __init__(self, parent):
        super(ExportWindow, self).__init__()
        self.parent = parent
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.active_window = None
        self._setup()
        self._createActions()
        self._connectActions()

        self.filetype = 'png'
        self.colorbar = False
        self.rulers = False
        self.colormap = 'afmhot'
        self.scale_bar = True
        self.fontsize = 10

    def _setup(self):

        self.setObjectName("Export Data")
        self.setFixedSize(610, 640)
        self.setWindowTitle("Export")
        self.central_widget = QtWidgets.QWidget(self)
        self.layout_main = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout_2 = QtWidgets.QHBoxLayout(self.central_widget)
        self.layout_settings = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout_preview = QtWidgets.QVBoxLayout(self.central_widget)
        self.layout_buttons = QtWidgets.QHBoxLayout(self.central_widget)
        self.layout_2.addLayout(self.layout_preview)
        self.layout_2.addLayout(self.layout_settings)
        self.layout_main.addLayout(self.layout_2)
        self.layout_main.addLayout(self.layout_buttons)
        self.setCentralWidget(self.central_widget)

        self.canvas = FigureCanvas(self)
        self.canvas.setMinimumSize(400, 400)
        self.canvas.setMaximumSize(400, 400)
        self.layout_preview.addWidget(self.canvas)




    def _create_topography_filetypes(self):
        self.combobox_filetypes = QComboBox(self)
        self.combobox_filetypes.addItems(self.FILETYPES_TOPO)
        self.layout_settings.addWidget(self.combobox_filetypes)
        self.combobox_filetypes.currentIndexChanged.connect(self._filetype_text_changed)

    def _create_image_settings(self):
        self.setting_colorbar = QCheckBox('Colorbar', self)
        self.layout_settings.addWidget(self.setting_colorbar)

    def _filetype_text_changed(self, i):
        self.filetype = self.combobox_filetypes.currentText()

    def _colorbar_changed(self):
        self.colorbar = self.setting_colorbar.isChecked()
        self.draw()

    def _createActions(self):

        # Create apply button
        self.applyButton = QtWidgets.QPushButton("Apply", self)

        self.layout_buttons.addWidget(self.applyButton)
        self.applyButton.setObjectName("applyButton")

        # Create cancel button
        self.cancelButton = QtWidgets.QPushButton("Cancel", self)
        self.layout_buttons.addWidget(self.cancelButton)

        self.cancelButton.setObjectName("cancelButton")

    def _connectActions(self):
        self.cancelButton.clicked.connect(self.cancel)
        self.applyButton.clicked.connect(self.apply)

    def update(self):
        for i in reversed(range(self.layout_settings.count())):
            self.layout_settings.itemAt(i).widget().setParent(None)
        if self.parent.active_result_window is not None:
            self.active_window = self.parent.results_windows[self.parent.active_result_window]
            if isinstance(self.active_window, ResultWindow.TopographyWindow):
                self._create_topography_filetypes()
                self._create_image_settings()
            self.draw()

    def draw(self):
        self.canvas.axes.cla()
        im = self.canvas.axes.pcolormesh(self.active_window.data.X, self.active_window.data.Y, self.active_window.data.Z, cmap=self.colormap)
        if self.colorbar:
            self.canvas.fig.colorbar(im, ax=self.canvas.axes)
            self.canvas.axes.set_title(self.active_window.data.unit)
        if not self.rulers:
            self.canvas.axes.get_xaxis().set_visible(False)
            self.canvas.axes.get_yaxis().set_visible(False)
        if self.scale_bar:
            self._draw_scale_bar()
        if not self.colorbar and not self.rulers:
            self.canvas.axes.set_frame_on(False)
            self.canvas.axes.set_position([0., 0., 1, 1])
        self.canvas.axes.set_aspect('equal')
        self.canvas.draw()

    def _draw_scale_bar(self):
        shape = self.active_window.data.X.shape
        xrange = self.active_window.data.get_x_range()
        length = round(0.2 * xrange)
        text = str(length) + ' ' + self.active_window.data.xunit
        x1 = self.active_window.data.X[1, round(0.1 * shape[0])]
        x2 = self.active_window.data.X[1, round(0.3 * shape[0])]
        y1 = self.active_window.data.Y[round(0.12 * shape[0]), 1]
        y2 = self.active_window.data.Y[round(0.12 * shape[0]), 1]
        line = matplotlib.lines.Line2D([x1, x2],
                                       [y1, y2], linewidth=0.01 * shape[1],
                                       color='black')
        text = matplotlib.text.Text(x=self.active_window.data.X[1, round(0.2 * shape[0])], y=self.active_window.data.Y[round(0.15 * shape[1]), 1],
                                    text=text,
                                    horizontalalignment='center', fontsize=13)
        self.canvas.axes.add_line(line)
        self.canvas.axes.add_artist(text)

    def disable(self):
        self.applyButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)

    def apply(self):
        file, _ = QFileDialog.getSaveFileName(self, caption="Save .png", filter="Images (*.png)")
        self.canvas.fig.savefig(file, format = self.filetype)

    def cancel(self):
        self.hide()

    # Event handling
    def eventFilter(self, source, event):
        # Calling parent closing function on close
        if event.type() == QtCore.QEvent.Hide:
            self.parent.export_win_active = False
        return False

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        #self.axes.set_position([0.1, 0.2, 0.85, 0.78])
        super(FigureCanvas, self).__init__(self.fig)
