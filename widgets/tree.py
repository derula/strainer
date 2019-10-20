from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QTreeWidget, QSizePolicy


class Tree(QTreeWidget):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def sizeHint(self):
        return QSize(100, 300)
