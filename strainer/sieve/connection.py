from collections import deque

from PyQt5.QtCore import pyqtSignal, QMutex, QObject, Qt, QThread, QWaitCondition
from sievelib import managesieve

from ..types import TreeItemStatus


class SieveConnection(QObject):
    connecting = pyqtSignal()
    success = pyqtSignal(managesieve.Client)
    failure = pyqtSignal(str)

    def __init__(self, item, account=None, action=None):
        super().__init__()
        self._item = item
        self._account = account or item.value
        self.connecting.connect(self.setLoading, Qt.BlockingQueuedConnection)
        self.success.connect(self.setNormal, Qt.BlockingQueuedConnection)
        self.failure.connect(self.setError, Qt.BlockingQueuedConnection)
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

    def setLoading(self):
        self._item.setStatus(TreeItemStatus.Loading, 'Loading, please wait...')

    def setNormal(self, _):
        self._item.setStatus(TreeItemStatus.Normal)

    def setError(self, message):
        self._item.setStatus(TreeItemStatus.Error, message)

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
                self._tree.blockSignals(True)
                while self._queue:
                    self._queue.popleft().exec()
            finally:
                self._tree.blockSignals(False)