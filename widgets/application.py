from PyQt5.QtWidgets import QApplication

from . import actions
from .account_window import AccountWindow
from .main_window import MainWindow
from .menus import ManageMenu


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        all_actions = {}
        for action in actions.__all__:
            cls = getattr(actions, action)
            all_actions[cls] = cls(None)
        self._main_window = MainWindow(all_actions)
        self._main_window.show()

