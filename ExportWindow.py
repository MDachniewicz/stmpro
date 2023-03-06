from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QComboBox

import ResultWindow
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure

class ExportWindow(QMainWindow):
    FILETYPES_TOPO = ['png', 'mat']
    def __init__(self, parent):
        super(ExportWindow, self).__init__()
        self.parent = parent
        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.active_window = None
        self._setup()
        self._createActions()
        self._connectActions()

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
        self.canvas.setMinimumSize(400,400)
        self.canvas.setMaximumSize(400, 400)
        self.layout_preview.addWidget(self.canvas)




    def _create_topography_filetypes(self):
        self.combobox_filetypes = QComboBox(self)
        self.combobox_filetypes.addItems(self.FILETYPES_TOPO)
        self.layout_settings.addWidget(self.combobox_filetypes)

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
            self.parent.export_win_active = False
        return False

class FigureCanvas(FigureCanvasQTAgg):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.axes.set_position([0.1, 0.2, 0.85, 0.78])
        super(FigureCanvas, self).__init__(fig)
