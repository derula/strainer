from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QSplitter

from .editor import Editor
from .tree import Tree


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Strainer')
        frame = QFrame(self)
        layout = QHBoxLayout()
        splitter = QSplitter()
        splitter.addWidget(Tree())
        splitter.addWidget(Editor())
        layout.addWidget(splitter)
        frame.setLayout(layout)
        self.setCentralWidget(frame)

