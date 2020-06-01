from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, QHeaderView

from ...actions import *
from ...controls import AccountMenu, ScriptMenu
from .items import AccountItem


class Tree(QTreeWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setMinimumSize(QSize(100, 200))
        self.setColumnCount(2)
        self.header().setMinimumSectionSize(0)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.setHeaderHidden(True)
        self.setExpandsOnDoubleClick(False)
        self._accountMenu = AccountMenu(self.window())
        self._scriptMenu = ScriptMenu(self.window())
        for action in (*self._accountMenu.actions(), *self._scriptMenu.actions()):
            try:
                action.setDefaultArgs(lambda: (self.currentItem(),))
            except AttributeError:
                pass
        self.currentItemChanged.connect(self.onCurrentItemChanged)
        self.itemActivated.connect(self.onItemActivated)
        self.itemChanged.connect(self.onItemChanged)
        self._updateMenus()

    def sizeHint(self):
        return QSize(200, 600)

    def blockSignals(self, value):
        super().blockSignals(value)
        self._updateMenus(None if value else self.currentItem())

    def onCurrentItemChanged(self, next, previous):
        self._updateMenus(next)

    def _updateMenus(self, item=None):
        self._accountMenu.update(item)
        self._scriptMenu.update(item)

    def contextMenuEvent(self, event: QContextMenuEvent):
        item = self.itemAt(event.pos()) or self.currentItem()
        if not item:
            return
        if item.parent():
            self._scriptMenu.popup(event.globalPos())
        else:
            self._accountMenu.popup(event.globalPos())

    def onItemActivated(self, item):
        if isinstance(item, AccountItem):
            self.window().action(EditAccount).trigger(item)
        else:
            self.window().action(OpenScript).trigger(item)

    def onItemChanged(self, item):
        self.onItemsChanged([item])

    def onItemsChanged(self, items):
        self.sortItems(0, Qt.AscendingOrder)
        for item in items:
            if item.parent() is None:
                self.window().action(ReloadAccount).trigger(item)

    def addAccountItem(self, account):
        return self.addAccountItems([account])[0]

    def addAccountItems(self, accounts):
        if not accounts:
            return []
        items = [AccountItem(account) for account in accounts]
        super().addTopLevelItems(items)
        self.onItemsChanged(items)
        return items
