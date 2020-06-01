from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QTreeWidgetItem

from ...types import TreeItemStatus


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
