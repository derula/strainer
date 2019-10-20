from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QTreeWidget, QSizePolicy


class Tree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(100, 200))

    def sizeHint(self):
        return QSize(150, 300)
