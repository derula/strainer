from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QFrame, QLabel, QProgressBar, QSizePolicy, QStatusBar, QToolBar
from qtawesome import IconWidget

from ..actions import *
from .base import MyActionWidget


class MyToolBar(MyActionWidget, QToolBar):
    pass

class ManageToolBar(MyToolBar):
    _actions = [EditAccount, ReloadAccount, None, NewScript, RenameScript, None, OpenScript, ActivateScript]

class EditToolBar(MyToolBar):
    _actions = [SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent]

class NavigateToolBar(MyToolBar):
    _actions = [HomePage, None, PreviousPage, NextPage, ReloadPage]

class StatusBar(QStatusBar):
    def __init__(self, parent):
        super().__init__(parent)
        self._account = StatusBarPanel('{}', 'mdi.account')
        self._script = StatusBarPanel('{}', 'mdi.file')
        self._cursor = StatusBarPanel('{}:{}', 'mdi.cursor-text')
        self.addWidget(self._account)
        self.addWidget(self._script)
        self.addPermanentWidget(self._cursor)

    def setScript(self, item):
        if item is None:
            self._script.setText()
            self._account.setText()
        else:
            self._script.setText(item.name)
            self._account.setText(item.parent().name)

    def setCursorPosition(self, row, col):
        self._cursor.setText(row + 1, col + 1)

class StatusBarPanel(QFrame):
    def __init__(self, format_str, icon):
        super().__init__()
        self._addCaption = format_str.format
        self._numArgs = format_str.count('{}')
        self._caption = QLabel()
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(8, 0, 8, 0)
        self.layout().addWidget(IconWidget(icon))
        self.layout().addWidget(self._caption)
        self.setText()

    def setText(self, *newText):
        defaultValues = ('-' for _ in range(self._numArgs - len(newText)))
        self._caption.setText(self._addCaption(*newText, *defaultValues))
