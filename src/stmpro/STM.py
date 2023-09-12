import sys
from PyQt5.QtWidgets import QApplication
import STMgui

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = STMgui.MainWindow()
    win.show()
    sys.exit(app.exec())