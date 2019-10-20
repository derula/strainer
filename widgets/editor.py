from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QSizePolicy


class Editor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(QSize(300, 200))

    def sizeHint(self):
        return QSize(450, 300)
