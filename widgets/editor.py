from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QSizePolicy


class Editor(QsciScintilla):
    def __init__(self):
        super().__init__()
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Minimum)

    def sizeHint(self):
        return QSize(300, 300)
