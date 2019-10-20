from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QSplitter

from .editor import Editor
from .tree import Tree


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Strainer')
        splitter = QSplitter()
        splitter.addWidget(Tree())
        splitter.addWidget(Editor())
        self.setCentralWidget(splitter)

