# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:40:07 2022

@author: marek
"""

import sys
from PyQt5.QtWidgets import QApplication
import STMgui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = STMgui.MainWindow()
    win.show()
    sys.exit(app.exec())