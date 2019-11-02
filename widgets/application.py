from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QApplication
from sievelib import managesieve

from . import actions
from .menus import ManageMenu
from .tree import AccountStatus
from .windows import AccountWindow, MainWindow


class LoadScriptsThread(QThread):
    def __init__(self, tree, item):
        super().__init__()
        self._tree = tree
        self._item = item

    def run(self):
        _, server, port, login, passwd, starttls, authmech = self._item.value
        self._tree.blockSignals(True)
        try:
            self._item.setStatus(AccountStatus.Loading, 'Loading scripts from server...')
            conn = managesieve.Client(server, port)
            if not conn.connect(login, passwd, starttls=starttls, authmech=authmech):
                raise managesieve.Error('Failed to authenticate to server')
            self._item.replaceScriptItems(*conn.listscripts())
            self._item.setStatus(AccountStatus.Normal)
        except managesieve.Error as e:
            self._item.setStatus(AccountStatus.Error, e.args[0])
        except Exception:
            self._item.setStatus(AccountStatus.Normal)
            raise
        finally:
            self._tree.blockSignals(False)
        self._tree.update(self._tree.indexFromItem(self._item, 1))

class Application(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        all_actions = {}
        for action in actions.__all__:
            cls = getattr(actions, action)
            all_actions[cls] = cls(None)
        self._mainWindow = MainWindow(all_actions)
        for action in ('addAccount', 'editAccount', 'removeAccount', 'reloadAccount'):
            getattr(self._mainWindow.tree, action).connect(getattr(self, action))
        self._mainWindow.show()
        self._accountWindow = AccountWindow(self._mainWindow)
        self._loadScriptsThread = None

    def addAccount(self):
        result = self._accountWindow.exec()
        if result is not None:
            self._mainWindow.tree.addAccountItem(result)
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

    def reloadAccount(self, item):
        if self._loadScriptsThread is not None:
            self._loadScriptsThread.exit()
        self._loadScriptsThread = LoadScriptsThread(self._mainWindow.tree, item)
        self._loadScriptsThread.start()
