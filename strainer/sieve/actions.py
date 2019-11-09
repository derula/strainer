from sievelib import managesieve

from .connection import SieveConnection
from ..types import AccountStatus


class LoadScripts(SieveConnection):
    def __init__(self, tree, item):
        self._tree = tree
        self._item = item
        super().__init__(item.value)

    def run(self):
        self._tree.blockSignals(True)
        self._item.setStatus(AccountStatus.Loading, 'Loading scripts from server...')
        super().run()

    def _success(self, conn):
        self._item.replaceScriptItems(*conn.listscripts())
        self._item.setStatus(AccountStatus.Normal)

    def _failure(self, e):
        if isinstance(e, managesieve.Error):
            self._item.setStatus(AccountStatus.Error, e.args[0])
        else:
            self._item.setStatus(AccountStatus.Normal)
            return e

    def _always(self):
        self._tree.blockSignals(False)
        self._tree.update(self._tree.indexFromItem(self._item, 1))
