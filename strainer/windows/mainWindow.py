from PyQt5.QtCore import Qt, QSettings, QSize
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QMainWindow, QSplitter, QStyle

from ..controls import ManageMenu, EditMenu, NavigateMenu, ManageToolBar, EditToolBar, NavigateToolBar, StatusBar
from ..widgets import Tree, Editor, Reference
from .messages import ConfirmCloseMessage


class MainWindow(QMainWindow):
    def __init__(self, all_actions):
        super().__init__()
        self._actions = all_actions

        self._splitter = QSplitter()
        self.setCentralWidget(QFrame(self))
        QHBoxLayout(self.centralWidget()).addWidget(self._splitter)

        self.menuBar().addMenu(ManageMenu(self))
        self.menuBar().addMenu(EditMenu(self))
        self.menuBar().addMenu(NavigateMenu(self))
        self.addToolBar(ManageToolBar(self))
        self.addToolBar(EditToolBar(self))
        self.addToolBar(NavigateToolBar(self))
        self.setStatusBar(StatusBar(self))

        self._tree = Tree(self._splitter)
        self._editor = Editor(self._splitter)
        self._reference = Reference(self._splitter)
        self.statusBar().gotoError.connect(self._editor.setCursorPosition)
        self.statusBar().gotoError.connect(lambda *_: self._editor.setFocus(Qt.OtherFocusReason))
        self.statusBar().errorChanged.connect(self._editor.setParseError)
        self._editor.modificationChanged.connect(self.onModificationChanged)
        self._editor.cursorPositionChanged.connect(self.statusBar().setCursorPosition)
        self._editor.textChanged.connect(lambda: self.statusBar().parseScript(self._editor.text()))
        self._openScript = None
        self._confirmClose = ConfirmCloseMessage(self).exec

        self.onModificationChanged()

    def show(self, desktop):
        settings = QSettings()
        try:
            self.restoreGeometry(settings.value('windows/main/geometry'))
        except TypeError:
            geometry = desktop.availableGeometry()
            size = geometry.size()
            size = QSize(size.width() * 0.75, size.height() * 0.75)
            self.setGeometry(QStyle.alignedRect(Qt.LeftToRight, Qt.AlignCenter, size, geometry))
        try:
            self.restoreState(settings.value('windows/main/window-state'))
        except TypeError:
            pass
        try:
            self._splitter.restoreState(settings.value('windows/main/splitter-state'))
        except TypeError:
            pass
        super().show()

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

    def onModificationChanged(self, isModified=False):
        title = 'Strainer'
        if self._openScript:
            title = f"{title} ({self._openScript.parent().name}: {self._openScript.name}{'*' if isModified else ''})"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self._confirmClose():
            settings = QSettings()
            settings.setValue('windows/main/splitter-state', self._splitter.saveState())
            settings.setValue('windows/main/window-state', self.saveState())
            settings.setValue('windows/main/geometry', self.saveGeometry())
            event.accept()
        else:
            event.ignore()
