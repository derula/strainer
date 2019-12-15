from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QBrush, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView

from ..types import Account, TreeItemStatus


class TreeItem(QTreeWidgetItem):
    _STATUSES = {
        TreeItemStatus.Normal: ('', None),
        TreeItemStatus.Loading: ('…', None),
        TreeItemStatus.Error: ('!', 'red'),
    }

    def __init__(self, texts):
        super().__init__(texts)
        self.setStatus(TreeItemStatus.Normal)

    def setStatus(self, status, toolTip=''):
        text, color = self._STATUSES[status]
        brush = self.foreground(0)
        if color:
            brush.setColor(QColor(color))
        self.setText(1, text)
        self.setForeground(1, brush)
        self.setToolTip(1, toolTip)
        self._status = status

    @property
    def status(self):
        return self._status

class AccountItem(TreeItem):
    def __init__(self, value):
        super().__init__(['', ''])
        self.value = value

    @property
    def value(self):
        return Account(self.text(0), *self.data(0, Qt.UserRole))

    @value.setter
    def value(self, value):
        text, *value = value
        self.setText(0, text)
        self.setData(0, Qt.UserRole, value)

    def replaceScriptItems(self, activeScript, inactiveScripts):
        self.takeChildren()
        self.addChild(ScriptItem(activeScript, True))
        self.addChildren(ScriptItem(script) for script in inactiveScripts)
        self.sortChildren(0, Qt.AscendingOrder)
        self.setExpanded(True)

class ScriptItem(TreeItem):
    def __init__(self, value, active=False):
        self._active = active
        super().__init__([value, ''])

    def setStatus(self, status, tooltip=''):
        super().setStatus(status, tooltip)
        self._applyActiveState()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self._applyActiveState()

    def _applyActiveState(self):
        if self._active and self._status == TreeItemStatus.Normal:
            self.setText(1, '*')

class Tree(QTreeWidget):
    addAccount = pyqtSignal()
    editAccount = pyqtSignal(AccountItem)
    removeAccount = pyqtSignal(AccountItem)
    reloadAccount = pyqtSignal(AccountItem)
    newScript = pyqtSignal()
    openScript = pyqtSignal(ScriptItem)
    deleteScript = pyqtSignal(ScriptItem)
    activateScript = pyqtSignal(ScriptItem)

    def __init__(self, menu):
        super().__init__()
        self.setMinimumSize(QSize(100, 200))
        self.setColumnCount(2)
        self.header().setMinimumSectionSize(0)
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(0, QHeaderView.Stretch)
        self.header().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.setHeaderHidden(True)
        self._menu = menu
        self._signals = tuple(f'{name[0].lower()}{name[1:]}' for name in (a.__class__.__name__ for a in menu.actions))
        for action, name in zip(menu.actions, self._signals):
            action.triggered.connect(self._signalHandler(name))
        self.currentItemChanged.connect(self.onCurrentItemChanged)
        self.itemActivated.connect(self.onItemActivated)
        self.itemChanged.connect(self.onItemChanged)
        menu.update(None)

    def _signalHandler(self, name):
        signal = getattr(self, name)
        if '()' in signal.signal:
            return lambda event: getattr(self, name).emit()
        else:
            return lambda event: getattr(self, name).emit(self.currentItem())

    def sizeHint(self):
        return QSize(150, 300)

    def blockSignals(self, value):
        super().blockSignals(value)
        self._menu.update(False if value else self.currentItem())

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

    def connectSignals(self, target):
        for signal in self._signals:
            try:
                getattr(self, signal).connect(getattr(target, signal))
            except AttributeError:
                pass

    def addAccountItem(self, account):
        return self.addAccountItems([account])[0]

    def addAccountItems(self, accounts):
        if not accounts:
            return []
        items = [AccountItem(account) for account in accounts]
        super().addTopLevelItems(items)
        self.onItemsChanged(items)
        self.setCurrentItem(items[0])
        return items
