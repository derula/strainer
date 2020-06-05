from collections import deque

from PyQt5.QtCore import pyqtSignal, QMutex, QObject, Qt, QThread
from PyQt5.QtWidgets import QMessageBox
from sievelib import managesieve

from ..types import TreeItemStatus


class SieveConnection(QObject):
    connecting = pyqtSignal()
    success = pyqtSignal(managesieve.Client)
    failure = pyqtSignal(str)
    cleanup = pyqtSignal()

    def __init__(self, item, account=None, action=None):
        super().__init__()
        self._item = item
        self._account = account or item.value
        self.connecting.connect(self.setLoading, Qt.BlockingQueuedConnection)
        self.success.connect(self.setNormal, Qt.BlockingQueuedConnection)
        self.failure.connect(self.setError, Qt.BlockingQueuedConnection)
        self.cleanup.connect(self.clearMessage, Qt.BlockingQueuedConnection)
        if action is not None:
            self.success.connect(action, Qt.BlockingQueuedConnection)

    def exec(self):
        server, port, login, passwd, starttls, authmech = self._account[1:]
        client = managesieve.Client(server, port)
        try:
            self.connecting.emit()
            if not client.connect(login, passwd, starttls=starttls, authmech=authmech):
                raise managesieve.Error('Failed to authenticate to server')
            self.success.emit(client)
        except managesieve.Error as e:
            self.failure.emit(e.args[0])
        finally:
            self.cleanup.emit()

    def setLoading(self):
        self._item.setStatus(TreeItemStatus.Loading, 'Loading, please wait...')
        self._item.treeWidget().window().statusBar().showMessage(f'Communicating with {self._account[1]}, please wait...')

    def setNormal(self, _):
        self._item.setStatus(TreeItemStatus.Normal)

    def setError(self, message):
        self._item.setStatus(TreeItemStatus.Error, message)

    def clearMessage(self):
        self._item.treeWidget().window().statusBar().clearMessage()

class SieveConnectionQueue(QThread):
    def __init__(self, tree):
        super().__init__()
        self._tree = tree
        self._triggered = QMutex()
        self._triggered.lock()
        self._queue = deque()
        self.start()

    def enqueue(self, item, account=None, action=None):
        self._queue.append(SieveConnection(item, account, action))
        self._triggered.unlock()

    def run(self):
        while True:
            while not self._queue:
                self._triggered.lock()
            try:
                self._tree().blockSignals(True)
                while self._queue:
                    self._queue.popleft().exec()
            finally:
                self._tree().blockSignals(False)

class SieveErrorChecker:
    def __init__(self, action, reaction):
        self._action = action
        self._reaction = reaction

    def __call__(self, client):
        result = self._action(client)
        if result is None or result is False:
            SieveErrorMessage(client).exec()
        else:
            self._reaction(result)

class SieveErrorMessage(QMessageBox):
    _texts = (
        'Failed to run given ManageSieve command.',
        'If the problem persists, try reloading the account.'
    )

    def __init__(self, client):
        texts = list(self._texts)
        try:
            message = client.errmsg
            try:
                message = message.decode('utf-8')
            except AttributeError:
                pass
            texts.insert(1, f'Reason: {message}')
        except AttributeError:
            pass
        super().__init__(QMessageBox.Critical, 'ManageSieve error', '\n'.join(texts), QMessageBox.Ok)
