from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from . import actions
from .menus import ManageMenu
from .tree import TreeItem
from .windows import AccountWindow, MainWindow


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        all_actions = {}
        for action in actions.__all__:
            cls = getattr(actions, action)
            all_actions[cls] = cls(None)
        self._mainWindow = MainWindow(all_actions)
        self._mainWindow.tree.addAccount.connect(self.addAccount)
        self._mainWindow.tree.editAccount.connect(self.editAccount)
        self._mainWindow.tree.removeAccount.connect(self.removeAccount)
        self._mainWindow.show()
        self._accountWindow = AccountWindow(self._mainWindow)

    def addAccount(self):
        result = self._accountWindow.exec()
        if result is not None:
            item = TreeItem(result)
            self._mainWindow.tree.addTopLevelItem(item)
            self._mainWindow.tree.setCurrentItem(item)
        self._mainWindow.tree.setFocus(Qt.PopupFocusReason)

    def editAccount(self, item):
        result = self._accountWindow.exec(item.value)
        if result is not None:
            item.value = result
            self._mainWindow.tree.setCurrentItem(item)
        self._mainWindow.tree.setFocus(Qt.PopupFocusReason)

    def removeAccount(self, item):
        tree = self._mainWindow.tree
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
