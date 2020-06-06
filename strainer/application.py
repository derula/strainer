from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtWidgets import QApplication
from qtawesome import icon

from . import actions
from .config import Accounts
from .sieve import SieveConnectionQueue, SieveErrorChecker
from .windows import *

class Application(QApplication):
    def __init__(self, argv):
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
        self.setOrganizationName('incertitu.de')
        self.setApplicationName('strainer')
        self.setWindowIcon(icon('mdi.filter'))
        QSettings.setDefaultFormat(QSettings.IniFormat)
        self._mainWindow = MainWindow(all_actions)
        self._sieveQueue = SieveConnectionQueue(self._mainWindow.tree())
        self._accountDialog = AccountDialog(self._mainWindow)
        self._scriptNameDialog = ScriptNameDialog(self._mainWindow)
        self._mainWindow.show(self.desktop())
        self._accounts = Accounts()
        self._mainWindow.tree().addAccountItems(list(self._accounts.all))

    def addAccount(self):
        result = self._accountDialog.exec()
        if result is not None:
            item = self._mainWindow.tree().addAccountItem(result)
            self._accounts.add(item.value)
        self._mainWindow.tree().setFocus(Qt.PopupFocusReason)

    def editAccount(self, item):
        item = item.parent() or item
        old_value = item.value
        result = self._accountDialog.exec(old_value)
        if result is not None:
            item.value = result
            self._mainWindow.tree().setCurrentItem(item)
            self._accounts.update(old_value.name, item.value)
        self._mainWindow.tree().setFocus(Qt.PopupFocusReason)

    def removeAccount(self, item):
        item = item.parent() or item
        tree = self._mainWindow.tree()
        if ConfirmRemoveAccount(self._mainWindow).exec(item.name):
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
            self._accounts.remove(item.value)

    def reloadAccount(self, item):
        item = item.parent() or item
        openScript = self._mainWindow.openScript()
        if not openScript or openScript.parent() != item or self._mainWindow.setOpenScript(None):
            self._sieveQueue.enqueue(item, action=SieveErrorChecker(
                lambda client: client.listscripts(),
                lambda result: item.replaceScriptItems(*result)
            ))

    def newScript(self, item):
        item = item.parent() or item
        scriptName = self._scriptNameDialog.exec(item)
        self._mainWindow.tree().setFocus(Qt.PopupFocusReason)
        if scriptName is not None:
            self._sieveQueue.enqueue(item, action=SieveErrorChecker(
                lambda client: client.putscript(scriptName, ''),
                lambda _: self._mainWindow.tree().setCurrentItem(item.addScriptItem(scriptName))
            ))

    def renameScript(self, item):
        account = item.parent() or item
        scriptName = self._scriptNameDialog.exec(account, item.name)
        self._mainWindow.tree().setFocus(Qt.PopupFocusReason)
        if scriptName is not None:
            self._sieveQueue.enqueue(item, account.value, SieveErrorChecker(
                lambda client: client.renamescript(item.name, scriptName),
                lambda _: item.setText(0, scriptName)  # because assignment is syntactically invalid in a lambda
            ))

    def deleteScript(self, item):
        account = item.parent()
        if ConfirmDeleteScript(self._mainWindow).exec(item.name, account.name):
            if item == self._mainWindow.openScript():
                self._mainWindow.setOpenScript(None, force=True)
            self._sieveQueue.enqueue(item, account.value, SieveErrorChecker(
                lambda client: client.deletescript(item.name),
                lambda _: account.takeChild(account.indexOfChild(item))
            ))

    def openScript(self, item):
        if self._mainWindow.setOpenScript(None):
            self._sieveQueue.enqueue(item, item.parent().value, SieveErrorChecker(
                lambda client: client.getscript(item.name),
                lambda result: self._mainWindow.setOpenScript(item, result)
            ))

    def activateScript(self, item):
        itemName = '' if item.active else item.name
        self._sieveQueue.enqueue(item, item.parent().value, SieveErrorChecker(
            lambda client: client.setactive(item.name),
            lambda _: item.parent().setActiveScript(item)
        ))

    def saveDocument(self):
        script = self._mainWindow.openScript()
        text = self._mainWindow.editor().text()
        if script:
            self._sieveQueue.enqueue(script, script.parent().value, SieveErrorChecker(
                lambda client: client.putscript(script.name, text),
                lambda _: self._mainWindow.editor().setModified(text != self._mainWindow.editor().text())
            ))
