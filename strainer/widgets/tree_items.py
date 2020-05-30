from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QTreeWidgetItem

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
