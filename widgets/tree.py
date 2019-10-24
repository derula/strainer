from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem


class Tree(QTreeWidget):
    def __init__(self, menu):
        super().__init__()
        self.setMinimumSize(QSize(100, 200))
        self.setHeaderHidden(True)
        menu.relatesTo(self)
        self._menu = menu

    def sizeHint(self):
        return QSize(150, 300)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self._menu.popup(event.globalPos())

class TreeItem(QTreeWidgetItem):
    def __init__(self, value):
        super().__init__([''])
        self.value = value

    @property
    def value(self):
        return [self.text(0), *self.data(0, Qt.UserRole)]

    @value.setter
    def value(self, value):
        text, *value = value
        self.setText(0, text)
        self.setData(0, Qt.UserRole, value)
