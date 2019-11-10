from PyQt5.QtCore import QThread
from sievelib import managesieve

from .types import TreeItemStatus


class SieveConnection(QThread):
    _TOOLTIP_LOADING: str

    def __init__(self, tree, item, account=None, action=None):
        super().__init__()
        self._tree = tree
        self._item = item
        self._account = account or item.value
        self._action = action
        self.start()

    def run(self):
        _, server, port, login, passwd, starttls, authmech = self._account
        self._tree.blockSignals(True)
        self._item.setStatus(TreeItemStatus.Loading, 'Loading, please wait...')
        try:
            conn = managesieve.Client(server, port)
            if not conn.connect(login, passwd, starttls=starttls, authmech=authmech):
                raise managesieve.Error('Failed to authenticate to server')
            if self._action is not None:
                self._action(conn)
            self._item.setStatus(TreeItemStatus.Normal)
        except managesieve.Error as e:
            self._item.setStatus(TreeItemStatus.Error, e.args[0])
        except Exception as e:
            self._item.setStatus(TreeItemStatus.Normal)
            raise e
        finally:
            self._tree.blockSignals(False)
            self._tree.update(self._tree.indexFromItem(self._item, 1))
