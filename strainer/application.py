from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QApplication, QStyle
from sievelib import managesieve

from . import actions
from .sieve import SieveConnectionQueue
from .windows import AccountWindow, ConfirmClose, MainWindow


class Application(QApplication):
    def __init__(self, argv, accounts):
        super().__init__(argv)
        all_actions = {}
        for action in actions.__all__:
            cls = getattr(actions, action)
            action = cls(None)
            name = f'{cls.__name__[0].lower()}{cls.__name__[1:]}'
            try:
                action.triggered.connect(getattr(self, name))
            except AttributeError:
                pass
            all_actions[cls] = action
        self._accounts = accounts
        self._openScript = None
        self._mainWindow = MainWindow(all_actions)
        self._sieveQueue = SieveConnectionQueue(self._mainWindow.tree)
        self._accountWindow = AccountWindow(self._mainWindow)
        self._mainWindow.tree().addAccountItems(list(accounts.all))
        geometry = self.desktop().availableGeometry()
        size = geometry.size()
        size = QSize(size.width() * 0.75, size.height() * 0.75)
        self._mainWindow.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, size, geometry))
        self._mainWindow.show()

    def addAccount(self):
        result = self._accountWindow.exec()
        if result is not None:
            item = self._mainWindow.tree().addAccountItem(result)
            self._accounts.add(item.value)
        self._mainWindow.tree().setFocus(Qt.PopupFocusReason)

    def editAccount(self, item):
        item = item.parent() or item
        old_value = item.value
        result = self._accountWindow.exec(old_value)
        if result is not None:
            item.value = result
            self._mainWindow.tree().setCurrentItem(item)
            self._accounts.update(old_value.name, item.value)
        self._mainWindow.tree().setFocus(Qt.PopupFocusReason)

    def removeAccount(self, item):
        item = item.parent() or item
        tree = self._mainWindow.tree()
        tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
        self._accounts.remove(item.value)

    def reloadAccount(self, item):
        item = item.parent() or item
        openScript = None
        if self._openScript and self._openScript.parent() == item:
            if not self.closeScript():
                return
        self._sieveQueue.enqueue(item, action=lambda client: item.replaceScriptItems(*client.listscripts()))

    def openScript(self, item):
        if not self.closeScript():
            return
        def loadScript(client):
            self._openScript = item
            self._openScript.open = True
            self._mainWindow.editor().open(client.getscript(item.text(0)), item.text(0))
        self._sieveQueue.enqueue(item, item.parent().value, loadScript)

    def saveScript(self):
        ...

    def closeScript(self):
        if not ConfirmClose(self._mainWindow.editor()).exec():
            return False
        if self._openScript:
            self._mainWindow.editor().close()
            self._openScript.open = False
            self._openScript = None
        return True
