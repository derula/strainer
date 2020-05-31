from PyQt5.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QSplitter
from qtawesome import icon

from ..controls import *
from ..widgets import *
from .messages import ConfirmCloseMessage


class MainWindow(QMainWindow):
    def __init__(self, all_actions):
        super().__init__()
        self._actions = all_actions

        splitter = QSplitter()
        self.setCentralWidget(QFrame(self))
        QHBoxLayout(self.centralWidget()).addWidget(splitter)

        self.setWindowIcon(icon('mdi.filter'))
        self.menuBar().addMenu(AccountMenu(self))
        self.menuBar().addMenu(ScriptMenu(self))
        self.menuBar().addMenu(EditMenu(self))
        self.addToolBar(Toolbar(self))

        self._tree = Tree(splitter)
        self._editor = Editor(splitter)
        self._reference = Reference(splitter)
        self._editor.modificationChanged.connect(self.onModificationChanged)
        self.onModificationChanged()

    def action(self, action_type):
        return self._actions[action_type]

    def tree(self):
        return self._tree

    def editor(self):
        return self._editor

    def reference(self):
        return self._reference

    def onModificationChanged(self, isModified=False):
        title = 'Strainer'
        if self._editor.scriptName:
            title = f"{title} ({self._editor.scriptName}{'*' if isModified else ''})"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        if ConfirmCloseMessage(self._editor).exec():
            event.accept()
        else:
            event.ignore()
