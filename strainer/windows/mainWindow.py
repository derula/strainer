from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QSplitter, QProgressBar, QLabel
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
        self.menuBar().addMenu(ManageMenu(self))
        self.menuBar().addMenu(EditMenu(self))
        self.menuBar().addMenu(NavigateMenu(self))
        self.addToolBar(ManageToolBar(self))
        self.addToolBar(EditToolBar(self))
        self.addToolBar(NavigateToolBar(self))
        self.setStatusBar(StatusBar(self))

        self._tree = Tree(splitter)
        self._editor = Editor(splitter)
        self._reference = Reference(splitter)
        self.statusBar().gotoError.connect(self.onGotoError)
        self._editor.modificationChanged.connect(self.onModificationChanged)
        self._editor.cursorPositionChanged.connect(self.statusBar().setCursorPosition)
        self._editor.textChanged.connect(lambda: self.statusBar().parseScript(self._editor.text()))
        self._openScript = None
        self._confirmClose = ConfirmCloseMessage(self).exec

        self.onModificationChanged()

    def action(self, action_type):
        return self._actions[action_type]

    def tree(self):
        return self._tree

    def editor(self):
        return self._editor

    def reference(self):
        return self._reference

    def openScript(self):
        return self._openScript

    def setOpenScript(self, item, content='', *, force=False):
        if self._openScript:
            if not force and not self._confirmClose():
                self._editor.setFocus(Qt.OtherFocusReason)
                return False
            self._openScript.open = False
            self._openScript = None
            self._editor.close()
        if item:
            self._editor.open(content)
            self._openScript = item
            self._openScript.open = True
        self.statusBar().setScript(self._openScript)
        self.onModificationChanged(False)
        return True

    def onGotoError(self, line):
        self._editor.setCursorPosition(line - 1, 0)
        self._editor.setFocus(Qt.OtherFocusReason)

    def onModificationChanged(self, isModified=False):
        title = 'Strainer'
        if self._openScript:
            title = f"{title} ({self._openScript.parent().name}: {self._openScript.name}{'*' if isModified else ''})"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self._confirmClose():
            event.accept()
        else:
            event.ignore()
