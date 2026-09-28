import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("PHANTOM VISION LAB")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
