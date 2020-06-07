from collections import deque
from dataclasses import dataclass

from PyQt5.QtCore import pyqtSignal, QMutex, QObject, Qt, QThread
from PyQt5.QtWidgets import QMessageBox, QTreeWidget, QTreeWidgetItem
from sievelib import managesieve

from ..types import Account, TreeItemStatus

@dataclass
class SieveConnectionInfo:
    thread: QThread
    account: Account
    item: QTreeWidgetItem
    action: callable = None
    reaction: callable = None

class SieveConnection(QObject):
    connecting = pyqtSignal()
    connectionError = pyqtSignal(str)
    success = pyqtSignal(object)
    failure = pyqtSignal(managesieve.Client)
    cleanup = pyqtSignal()

    def __init__(self, tree, info):
        super().__init__()
        self._tree = tree
        self._info = info
        self.moveToThread(info.thread)
        self.connecting.connect(self.onConnecting, Qt.BlockingQueuedConnection)
        self.connectionError.connect(self.onConnectionError, Qt.BlockingQueuedConnection)
        self.success.connect(self.onSuccess, Qt.BlockingQueuedConnection)
        self.failure.connect(self.onFailure, Qt.BlockingQueuedConnection)
        self.cleanup.connect(self.onCleanup, Qt.BlockingQueuedConnection)

    def exec(self):
        server, port, login, passwd, starttls, authmech = self._info.account[1:]
        client = managesieve.Client(server, port)
        try:
            tree = self._info.item.treeWidget()
            self.connecting.emit()
            if not client.connect(login, passwd, starttls=starttls, authmech=authmech):
                raise managesieve.Error('Failed to authenticate to server')
            result = self._info.action(client)
            if result is None or result is False:
                self.failure.emit(client)
            else:
                self.success.emit(result)
        except managesieve.Error as e:
            self.connectionError.emit(e.args[0])
        finally:
            self.cleanup.emit()

    def onConnecting(self):
        self._tree.blockSignals(True)
        self._tree.window().statusBar().showMessage(f'Communicating with {self._info.account[1]}, please wait...')
        self._info.item.setStatus(TreeItemStatus.Loading, 'Loading, please wait...')

    def onConnectionError(self, message):
        self._info.item.setStatus(TreeItemStatus.Error, message)

    def onSuccess(self, result):
        self._info.item.setStatus(TreeItemStatus.Normal)
        self._info.reaction(result)

    def onFailure(self, client):
        SieveErrorMessage(client).exec()

    def onCleanup(self):
        self._tree.window().statusBar().clearMessage()
        self._tree.blockSignals(False)

class SieveConnectionQueue(QThread):
    execSieve = pyqtSignal(SieveConnectionInfo)

    def __init__(self, tree):
        super().__init__()
        self._tree = tree
        self.moveToThread(self)
        self.execSieve.connect(self.onExec, Qt.QueuedConnection)
        self.start()

    def enqueue(self, item, action=None, reaction=None):
        account = (item.parent() or item).value
        info = SieveConnectionInfo(QThread.currentThread(), account, item, action, reaction)
        self.execSieve.emit(info)

    def onExec(self, info):
        SieveConnection(self._tree, info).exec()

class SieveErrorMessage(QMessageBox):
    _texts = (
        'Failed to run given ManageSieve command.',
        'If the problem persists, try reloading the account.'
    )

    def __init__(self, client):
        texts = list(self._texts)
        message = getattr(client, 'errmsg', None)
        try:
            message = message.decode('utf-8')
        except AttributeError:
            pass
        if message is not None:
            texts.insert(1, f'Reason: {message}')
        super().__init__(QMessageBox.Critical, 'ManageSieve error', '\n'.join(texts), QMessageBox.Ok)
