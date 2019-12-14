from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication
from sievelib import managesieve

from ..sieve import SieveConnection
from . import actions
from .menus import ManageMenu
from .windows import AccountWindow, MainWindow


class Application(QApplication):
    def __init__(self, argv, accounts):
        super().__init__(argv)
        all_actions = {}
        for action in actions.__all__:
            cls = getattr(actions, action)
            all_actions[cls] = cls(None)
        self._accounts = accounts
        self._sieveConnection = None
        self._mainWindow = MainWindow(all_actions)
        self._mainWindow.tree.connectSignals(self)
        self._mainWindow.tree.addAccountItems(accounts.all)
        self._mainWindow.show()
        self._accountWindow = AccountWindow(self._mainWindow)

    def addAccount(self):
        result = self._accountWindow.exec()
        if result is not None:
            item = self._mainWindow.tree.addAccountItem(result)
            self._accounts.add(item.value)
        self._mainWindow.tree.setFocus(Qt.PopupFocusReason)

    def editAccount(self, item):
        old_value = item.value
        result = self._accountWindow.exec(old_value)
        if result is not None:
            item.value = result
            self._mainWindow.tree.setCurrentItem(item)
            self._accounts.update(old_value.name, item.value)
        self._mainWindow.tree.setFocus(Qt.PopupFocusReason)

    def removeAccount(self, item):
        tree = self._mainWindow.tree
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
        self._accounts.remove(item.value)

    def reloadAccount(self, item):
        self._performSieveAction(item, lambda conn: item.replaceScriptItems(*conn.listscripts()))

    def openScript(self, item):
        self._performSieveAction(item, lambda conn: self._mainWindow.editor.setText(conn.getscript(item.text(0))))

    def _performSieveAction(self, item, action):
        account = (item.parent() or item).value
        if self._sieveConnection is not None:
            self._sieveConnection.exit()
        self._sieveConnection = SieveConnection(self._mainWindow.tree, item, account, action=action)

