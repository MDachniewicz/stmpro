# -*- coding: utf-8 -*-
"""
Created on Wed Jun 29 13:40:07 2022

@author: marek
"""
import sys
import STM_gui as gui


if __name__ == "__main__":
    app = gui.QApplication(sys.argv)
    win = gui.Window()
    win.show()
    sys.exit(app.exec())