from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

from . import actions
from .account_window import AccountWindow
from .main_window import MainWindow
from .menus import ManageMenu
from .tree import TreeItem


class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        all_actions = {}
        for action in actions.__all__:
            cls = getattr(actions, action)
            all_actions[cls] = cls(None)
        self._main_window = MainWindow(all_actions)
        self._account_window = AccountWindow(self._main_window)
        self._main_window.show()
        all_actions[actions.AddAccount].triggered.connect(self.onAddAccountTriggered)
        all_actions[actions.EditAccount].triggered.connect(self.onEditAccountTriggered)
        all_actions[actions.RemoveAccount].triggered.connect(self.onRemoveAccountTriggered)
        self._main_window.tree.itemDoubleClicked.connect(self.onTreeItemDoubleClicked)

    def onAddAccountTriggered(self, event):
        result = self._account_window.exec()
        if result is not None:
            self._main_window.tree.addTopLevelItem(TreeItem(result))

    def onEditAccountTriggered(self, event):
        self.editAccount(self._main_window.tree.currentItem())

    def onTreeItemDoubleClicked(self, item):
        if item.parent() is None:
            self.editAccount(item)

    def onRemoveAccountTriggered(self, event):
        tree = self._main_window.tree
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(tree.currentItem()))

    def editAccount(self, item):
        result = self._account_window.exec(item.value)
        if result is not None:
            item.value = result
