from PyQt5.QtCore import QSize
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QTreeWidget, QTreeWidgetItem

from .menus import ManageMenu


class Tree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(100, 200))
        self.setHeaderHidden(True)
        self.menu = ManageMenu(self)

    def sizeHint(self):
        return QSize(150, 300)

    def contextMenuEvent(self, event: QContextMenuEvent):
        self.menu.popup(event.globalPos())
