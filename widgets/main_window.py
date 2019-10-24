from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QSplitter

from .actions import *
from .editor import Editor
from .menus import ManageMenu
from .tree import Tree


class MainWindow(QMainWindow):
    def __init__(self, all_actions):
        super().__init__()
        self.setWindowTitle('Strainer')

        manage_menu = ManageMenu(self, all_actions)
        self.menuBar().addMenu(manage_menu)

        frame = QFrame(self)
        layout = QHBoxLayout()
        splitter = QSplitter()
        tree = Tree(manage_menu)
        splitter.addWidget(tree)
        splitter.addWidget(Editor())
        layout.addWidget(splitter)
        frame.setLayout(layout)
        self.setCentralWidget(frame)
        self._tree = tree

    @property
    def tree(self):
        return self._tree
