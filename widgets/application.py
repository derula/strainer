from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        self._window = MainWindow()
        self._window.show()
