from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
from sievelib import managesieve

from ..types import TreeItemStatus


class SieveConnection(QThread):
    success = pyqtSignal(managesieve.Client)
    failure = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, account):
        super().__init__()
        self._account = account

    def start(self, action=None):
        if action is not None:
            self.success.connect(action)
        self.finished.connect(lambda: self.success.disconnect(action))
        super().start()

    def run(self):
        server, port, login, passwd, starttls, authmech = self._account[1:]
        conn = managesieve.Client(server, port)
        try:
            if not conn.connect(login, passwd, starttls=starttls, authmech=authmech):
                self.failure.emit('Failed to authenticate to server')
            else:
                self.success.emit(conn)
        except managesieve.Error as e:
            self.failure.emit(e.args[0])
        finally:
            self.finished.emit()

class TreeSieveConnection(SieveConnection):
    def __init__(self, tree, item, account=None):
        super().__init__(account or item.value)
        self._tree = tree
        self._item = item
        self.finished.connect(self.unblock)
        self.success.connect(self.succeed)
        self.failure.connect(self.fail)

    def start(self, action=None):
        self._tree.blockSignals(True)
        self._item.setStatus(TreeItemStatus.Loading, 'Loading, please wait...')
        super().start(action)

    def unblock(self):
        self._tree.blockSignals(False)
        self._tree.update(self._tree.indexFromItem(self._item, 1))

    def succeed(self, conn):
        self._item.setStatus(TreeItemStatus.Normal)

    def fail(self, message):
        self._item.setStatus(TreeItemStatus.Error, message)
