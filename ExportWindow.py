from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QComboBox, QCheckBox, QSpinBox, QFileDialog

import ResultWindow
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.axes_grid1 import make_axes_locatable


class ExportWindow(QMainWindow):
    FILETYPES_TOPO = ['png', 'jpg']
    COLORMAPS = ['afmhot', 'hot', 'gist_heat', 'gist_gray']
    COLORS = ['black', 'white', 'blue', 'green']

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
        self.scalebar = True
        self.scalebar_color = 'black'
        self.scalebar_fontsize = 13
        self.dpi = 300
        self.fontsize = 10

    def _setup(self):

        self.setObjectName("Export Data")
        self.setFixedSize(710, 640)
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
        self.setting_colorbar.setChecked(self.colorbar)
        self.setting_colorbar.toggled.connect(self._colorbar_changed)
        self.layout_settings.addWidget(self.setting_colorbar)

        self.setting_colormap_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.label_colormap = QtWidgets.QLabel('Colormap:', self.central_widget)
        self.setting_colormap_layout.addWidget(self.label_colormap)
        self.setting_colormap = QComboBox(self.central_widget)
        self.setting_colormap.addItems(self.COLORMAPS)
        self.setting_colormap_layout.addWidget(self.setting_colormap)
        self.setting_colormap.currentTextChanged.connect(self._colormap_changed)
        self.layout_settings.addLayout(self.setting_colormap_layout)

        self.setting_scalebar_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.setting_scalebar = QCheckBox('Scalebar', self)
        self.setting_scalebar.setChecked(self.scalebar)
        self.setting_scalebar.toggled.connect(self._scalebar_changed)
        self.setting_scalebar_layout.addWidget(self.setting_scalebar)
        self.label_scalebar_color = QtWidgets.QLabel('Color:', self.central_widget)
        self.setting_scalebar_layout.addWidget(self.label_scalebar_color)
        self.setting_scalebar_color = QtWidgets.QComboBox(self.central_widget)
        self.setting_scalebar_color.addItems(self.COLORS)
        self.setting_scalebar_color.currentTextChanged.connect(self._scalebar_color_changed)
        self.setting_scalebar_layout.addWidget(self.setting_scalebar_color)
        self.label_scalebar_fontsize = QtWidgets.QLabel('Font size:', self.central_widget)
        self.setting_scalebar_layout.addWidget(self.label_scalebar_fontsize)
        self.setting_scalebar_fontsize = QtWidgets.QSpinBox(self.central_widget)
        self.setting_scalebar_fontsize.setRange(1, 60)
        self.setting_scalebar_fontsize.setValue(self.scalebar_fontsize)
        self.setting_scalebar_fontsize.valueChanged.connect(self._scalebar_fontsize_changed)
        self.setting_scalebar_layout.addWidget(self.setting_scalebar_fontsize)
        self.layout_settings.addLayout(self.setting_scalebar_layout)

        self.setting_ruler_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.setting_ruler = QCheckBox('Axes', self)
        self.setting_ruler.setChecked(self.rulers)
        self.setting_ruler.toggled.connect(self._ruler_changed)
        self.setting_ruler_layout.addWidget(self.setting_ruler)
        self.label_fontsize = QtWidgets.QLabel('Font size:', self.central_widget)
        self.setting_ruler_layout.addWidget(self.label_fontsize)
        self.setting_fontsize = QtWidgets.QSpinBox(self.central_widget)
        self.setting_fontsize.setRange(1, 60)
        self.setting_fontsize.setValue(self.fontsize)
        self.setting_fontsize.valueChanged.connect(self._fontsize_changed)
        self.setting_ruler_layout.addWidget(self.setting_fontsize)
        self.layout_settings.addLayout(self.setting_ruler_layout)

        self.setting_dpi_layout = QtWidgets.QHBoxLayout(self.central_widget)
        self.label_dpi = QtWidgets.QLabel('DPI: ', self.central_widget)
        self.setting_dpi = QtWidgets.QSpinBox(self.central_widget)
        self.setting_dpi.setRange(60, 1200)
        self.setting_dpi.setValue(self.dpi)
        self.setting_dpi.valueChanged.connect(self._dpi_changed)
        self.setting_dpi_layout.addWidget(self.label_dpi)
        self.setting_dpi_layout.addWidget(self.setting_dpi)
        self.layout_settings.addLayout(self.setting_dpi_layout)

    def _filetype_text_changed(self, i):
        self.filetype = self.combobox_filetypes.currentText()

    def _colorbar_changed(self):
        self.colorbar = self.setting_colorbar.isChecked()
        self.draw()

    def _colormap_changed(self, colormap):
        self.colormap = colormap
        self.draw()

    def _scalebar_changed(self):
        self.scalebar = self.setting_scalebar.isChecked()
        self.draw()

    def _scalebar_color_changed(self, color):
        self.scalebar_color = color
        self.draw()

    def _ruler_changed(self):
        self.rulers = self.setting_ruler.isChecked()
        self.draw()

    def _dpi_changed(self, value):
        self.dpi = value

    def _fontsize_changed(self, value):
        self.fontsize = value
        self.draw()

    def _scalebar_fontsize_changed(self, value):
        self.scalebar_fontsize = value
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
        self.canvas.fig.clf()
        self.canvas.axes = self.canvas.fig.add_subplot(111)
        im = self.canvas.axes.pcolormesh(self.active_window.data.X, self.active_window.data.Y,
                                         self.active_window.data.Z, cmap=self.colormap)
        self.canvas.axes.set_aspect('equal')
        if self.colorbar:
            divider = make_axes_locatable(self.canvas.axes)
            self.canvas.caxes = divider.append_axes("right", size="3%", pad=0.02)
            self.cb = self.canvas.fig.colorbar(im, cax=self.canvas.caxes)
            self.cb.ax.set_title(self.active_window.data.unit)
        if not self.rulers:
            self.canvas.axes.get_xaxis().set_visible(False)
            self.canvas.axes.get_yaxis().set_visible(False)
        else:
            self.canvas.axes.set_xlabel(f'x [{self.active_window.data.xunit}]', fontsize=self.fontsize)
            self.canvas.axes.set_ylabel(f'y [{self.active_window.data.xunit}]', fontsize=self.fontsize)
        if self.scalebar:
            self._draw_scale_bar()
        if not self.colorbar and not self.rulers:
            self.canvas.axes.set_frame_on(False)
            self.canvas.fig.tight_layout(pad=0)
        else:
            self.canvas.fig.tight_layout(rect=[0, 0.02, 1, 0.97])

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
                                       color=self.scalebar_color)
        text = matplotlib.text.Text(x=self.active_window.data.X[1, round(0.2 * shape[0])],
                                    y=self.active_window.data.Y[round(0.15 * shape[1]), 1],
                                    text=text,
                                    horizontalalignment='center', fontsize=self.scalebar_fontsize, color=self.scalebar_color)
        self.canvas.axes.add_line(line)
        self.canvas.axes.add_artist(text)

    def disable(self):
        self.applyButton.setDisabled(True)

    def enable(self):
        self.applyButton.setDisabled(False)

    def apply(self):
        file, _ = QFileDialog.getSaveFileName(self, caption=f'Save .{self.filetype}', filter=f'Images (*.{self.filetype})')
        self.canvas.fig.savefig(file, format=self.filetype, dpi=self.dpi)

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
        self.caxes = None
        # self.axes.set_position([0.1, 0.2, 0.85, 0.78])
        super(FigureCanvas, self).__init__(self.fig)
