import sys
from PyQt5.QtWidgets import QApplication
import stm_gui


def main():
    app = QApplication(sys.argv)
    win = STMgui.MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
