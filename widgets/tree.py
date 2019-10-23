from PyQt5.QtCore import QSize
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
