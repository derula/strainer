from enum import Enum, auto

from PyQt5.QtCore import Qt, QSize, pyqtSignal
from PyQt5.QtGui import QContextMenuEvent, QBrush, QColor
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem, QHeaderView


class TreeItem(QTreeWidgetItem):
    _STATUSES = {}
    _DEFAULT_STATUS = None

    def __init__(self, texts):
        super().__init__(texts)
        self._status = self._DEFAULT_STATUS

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


class AccountStatus(Enum):
    Normal = auto()
    Loading = auto()
    Error = auto()

class AccountItem(TreeItem):
    _STATUSES = {
        AccountStatus.Normal: ('', None),
        AccountStatus.Loading: ('…', None),
        AccountStatus.Error: ('!', 'red'),
    }
    _DEFAULT_STATUS = AccountStatus.Normal

    def __init__(self, value):
        super().__init__(['', ''])
        self.value = value

    @property
    def value(self):
        return [self.text(0), *self.data(0, Qt.UserRole)]

    @value.setter
    def value(self, value):
        text, *value = value
        self.setText(0, text)
        self.setData(0, Qt.UserRole, value)

    def replaceScriptItems(self, active_script, inactive_scripts):
        self.takeChildren()
        self.addChildren(
            ScriptItem(script, script == active_script) for script in sorted((active_script, *inactive_scripts))
        )
        self.sortChildren(0, Qt.AscendingOrder)

class ScriptStatus(Enum):
    Normal = auto()
    Active = auto()

class ScriptItem(TreeItem):
    _STATUSES = {
        ScriptStatus.Normal: ('', None),
        ScriptStatus.Active: ('*', None)
    }
    _DEFAULT_STATUS = ScriptStatus.Normal

    def __init__(self, value, active=False):
        super().__init__([value, ''])
        if active:
            self.setStatus(ScriptStatus.Active)

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
        for action in menu.actions():
            try:
                self.connectAction(action)
            except AttributeError:
                pass
        self.currentItemChanged.connect(self.onCurrentItemChanged)
        self.itemActivated.connect(self.onItemActivated)
        self.itemChanged.connect(self.onItemChanged)
        menu.update(None)

    def sizeHint(self):
        return QSize(150, 300)

    def blockSignals(self, value):
        super().blockSignals(value)
        self._menu.update(False if value else self.currentItem())

    def onCurrentItemChanged(self, next, previous):
        self._menu.update(next)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._menu.popup(event.globalPos())

    def connectAction(self, action):
        name = action.__class__.__name__
        signal = getattr(self, f'{name[0].lower()}{name[1:]}')
        if '()' in signal.signal:
            action.triggered.connect(lambda event: signal.emit())
        else:
            action.triggered.connect(lambda event: signal.emit(self.currentItem()))

    def onItemActivated(self, item):
        if isinstance(item, AccountItem):
            self.editAccount.emit(item)
        else:
            self.openScript.emit(item)

    def onItemChanged(self, item):
        self.sortItems(0, Qt.AscendingOrder)
        if item.parent() is None:
            self.reloadAccount.emit(item)

    def addAccountItem(self, value):
        item = AccountItem(value)
        super().addTopLevelItem(item)
        self.onItemChanged(item)
        self.setCurrentItem(item)
