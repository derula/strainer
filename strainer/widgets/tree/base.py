from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTreeWidgetItem
from qtawesome import icon, Spin

from ...types import TreeItemStatus


class TreeItem(QTreeWidgetItem):
    _STATUSES = {
        TreeItemStatus.Normal: (None, None),
        TreeItemStatus.Loading: ('mdi.progress-clock', None),
        TreeItemStatus.Error: ('mdi.alert', 'red'),
    }

    def __init__(self, texts):
        super().__init__(texts)
        self.setStatus(TreeItemStatus.Normal)

    def setStatus(self, status, toolTip=''):
        name, color = self._STATUSES[status]
        if not name:
            self.setIcon(1, icon())
        else:
            self.setIcon(1, icon(name, color=color))
        self.setToolTip(1, toolTip)
        self._status = status

    @property
    def name(self):
        return self.text(0)

    @name.setter
    def name(self, newValue):
        self.setText(0, newValue)
        if self.parent():
            self.parent().sortChildren(0, Qt.AscendingOrder)

    @property
    def status(self):
        return self._status
