from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, QHeaderView

from ..menus import ManageMenu
from .items import AccountItem, ScriptItem


class Tree(QTreeWidget):
    addAccount = pyqtSignal()
    editAccount = pyqtSignal(AccountItem)
    removeAccount = pyqtSignal(AccountItem)
    reloadAccount = pyqtSignal(AccountItem)
    newScript = pyqtSignal()
    openScript = pyqtSignal(ScriptItem)
    deleteScript = pyqtSignal(ScriptItem)
    activateScript = pyqtSignal(ScriptItem)

    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumSize(QSize(100, 200))
        self.setColumnCount(2)
        self.header().setMinimumSectionSize(0)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.setHeaderHidden(True)
        self._menu = ManageMenu(self.window())
        for action in self._menu.actions():
            try:
                signal = action.signal(self)
                if '()' not in signal.signal:
                    action.signalArgs(lambda: (self.currentItem(),))
            except AttributeError:
                pass
        self.currentItemChanged.connect(self.onCurrentItemChanged)
        self.itemActivated.connect(self.onItemActivated)
        self.itemChanged.connect(self.onItemChanged)
        self._menu.update()

    def sizeHint(self):
        return QSize(200, 600)

    def blockSignals(self, value):
        super().blockSignals(value)
        self._menu.update(None if value else self.currentItem())

    def onCurrentItemChanged(self, next, previous):
        self._menu.update(next)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._menu.popup(event.globalPos())

    def onItemActivated(self, item):
        if isinstance(item, AccountItem):
            self.editAccount.emit(item)
        else:
            self.openScript.emit(item)

    def onItemChanged(self, item):
        self.onItemsChanged([item])

    def onItemsChanged(self, items):
        self.sortItems(0, Qt.AscendingOrder)
        for item in items:
            if item.parent() is None:
                self.reloadAccount.emit(item)

    def addAccountItem(self, account):
        return self.addAccountItems([account])[0]

    def addAccountItems(self, accounts):
        if not accounts:
            return []
        items = [AccountItem(account) for account in accounts]
        super().addTopLevelItems(items)
        self.onItemsChanged(items)
        return items
