from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QFrame, QLabel, QStatusBar
from qtawesome import IconWidget
from sievelib.parser import Parser

from ..actions import *
from .base import MyActionWidget


class StatusBar(QStatusBar):
    errorChanged = pyqtSignal(int, int)
    gotoError = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self._account = StatusBarPanel('{}', 'mdi.account')
        self._script = StatusBarPanel('{}', 'mdi.file')
        self._error = ErrorPanel(self.errorChanged, self.gotoError)
        self._cursor = StatusBarPanel('{}:{}', 'mdi.cursor-text')
        self.addWidget(self._account)
        self.addWidget(self._script)
        self.addWidget(self._error)
        self.addPermanentWidget(self._cursor)

    def setScript(self, item):
        if item is None:
            self._script.setText()
            self._account.setText()
            self.parseScript(None)
        else:
            self._script.setText(item.name)
            self._account.setText(item.parent().name)

    def parseScript(self, text):
        self._error.parseScript(text)

    def setCursorPosition(self, row, col):
        self._cursor.setText(row + 1, col + 1)

class StatusBarPanel(QFrame):
    def __init__(self, format_str, *args, **kwargs):
        super().__init__()
        self._addCaption = format_str.format
        self._numArgs = format_str.count('{}')
        self._caption = QLabel()
        self._icon = IconWidget(*args, **kwargs)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(8, 0, 8, 0)
        self.layout().addWidget(self._icon)
        self.layout().addWidget(self._caption)
        self.setText()

    def setText(self, *newText):
        defaultValues = ('-' for _ in range(self._numArgs - len(newText)))
        self._caption.setText(self._addCaption(*newText, *defaultValues))

class ErrorPanel(StatusBarPanel):
    def __init__(self, changeSignal, gotoSignal):
        self._parser = Parser()
        super().__init__('{}', 'mdi.circle', color='gray')
        self._checkIcon = IconWidget('mdi.check-circle', color='green')
        self._errorIcon = IconWidget('mdi.close-circle', color='red')
        self._checkIcon.setVisible(False)
        self._errorIcon.setVisible(False)
        self.layout().insertWidget(1, self._checkIcon)
        self.layout().insertWidget(1, self._errorIcon)
        self._changeSignal = changeSignal
        self._caption.linkActivated.connect(lambda url: gotoSignal.emit(*self._errorPos))
        self._errorPos = (-1, -1)

    def parseScript(self, text=None):
        for widget in {self._icon, self._checkIcon, self._errorIcon}:
            widget.setVisible(False)
        errorPos = (-1, -1)
        if text is None:
            self._icon.setVisible(True)
            self.setText()
        elif self._parser.parse(text):
            self._checkIcon.setVisible(True)
            self.setText('No errors found in open script.')
        else:
            errorPos = (x - 1 for x in self._parser.error_pos)
            self._errorIcon.setVisible(True)
            self.setText(f'<a href="#"><span style="color:inherit;">{self._parser.error}</span></a>')
        if self._errorPos != errorPos:
            self._changeSignal.emit(*errorPos)
            self._errorPos = errorPos
