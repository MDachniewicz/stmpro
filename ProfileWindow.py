from PyQt5.QtWidgets import QDialog, QSlider, QLabel
from PyQt5 import QtCore, QtWidgets

class ProfileWindow(QDialog):  
    
    
    def __init__(self, parent):
        super(ProfileWindow, self).__init__()
        self.parent=parent
        self._setup(self)
        self._createActions()
        self._connectActions()
        
        self.profile_width = 3
        self._update()
        
    def _setup(self, Win):
        Win.setObjectName("Filter image")
        Win.setFixedSize(310, 440)
        Win.setWindowTitle("Filter")      
        
    def _createActions(self):
        self.slider = QSlider(QtCore.Qt.Orientation.Horizontal, self)
        self.slider.setGeometry(QtCore.QRect(20, 100, 150, 20))
        self.slider.setRange(1, 20)
        self.slider.setValue(3)
        self.slider.setSingleStep(1)
        
        self.profile_width_display = QLabel(f'Profile Width: {3}', self)
        self.profile_width_display.setGeometry(QtCore.QRect(180, 100, 80, 20))
        
        # Create apply button
        self.applyButton = QtWidgets.QPushButton("Apply", self)
        self.applyButton.setGeometry(QtCore.QRect(60, 330, 81, 41))
        self.applyButton.setObjectName("applyButton")
        
        #Create cancel button
        self.cancelButton = QtWidgets.QPushButton("Cancel", self)
        self.cancelButton.setGeometry(QtCore.QRect(170, 330, 81, 41))
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
        
    def index_changed(self, i):
        self.active_filter = i
        self._update()
        
    
        