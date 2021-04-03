from lark.exceptions import LarkError, UnexpectedInput
from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QStatusBar
from qtawesome import IconWidget

from ..sieve import parser


class StatusBar(QStatusBar):
    errorChanged = pyqtSignal(int, int)
    gotoError = pyqtSignal(int, int)

    def __init__(self, parent):
        super().__init__(parent)
        self._account = StatusBarPanel('{}', 'Account: {}', 'mdi.account')
        self._script = StatusBarPanel('{}', 'Script: {}', 'mdi.file')
        self._error = ErrorPanel(self.errorChanged, self.gotoError)
        self._cursor = StatusBarPanel('{}:{}', 'Cursor position: Line {}, Column {}', 'mdi.cursor-text')
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
    def __init__(self, caption_format, tooltip_format, *args, **kwargs):
        super().__init__()
        self._makeCaption = caption_format.format
        self._makeTooltip = tooltip_format.format
        self._numArgs = caption_format.count('{}')
        self._caption = QLabel()
        self._caption.minimumSizeHint = lambda: QSize(0, 0)
        self._icon = IconWidget(*args, **kwargs)
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(8, 0, 8, 0)
        self.layout().addWidget(self._icon)
        self.layout().addWidget(self._caption)
        self.setText()

    def setText(self, *newText):
        defaultValues = tuple('-' for _ in range(self._numArgs - len(newText)))
        self._caption.setText(self._makeCaption(*newText, *defaultValues))
        self.setToolTip(self._makeTooltip(*newText, *defaultValues))


class ErrorPanel(StatusBarPanel):
    def __init__(self, changeSignal, gotoSignal):
        super().__init__('{}', 'Syntax error check: {}', 'mdi.circle', color='gray')
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
        errorPos, fullError = self.getError(text)
        n_pos = fullError.find('\n')
        if n_pos > 0:
            error = fullError[:n_pos]
        else:
            error = fullError
        if errorPos is not None:
            error = f'<a href="#"><span style="color:inherit;">{error}</span></a>'
            self._errorIcon.setVisible(True)
        else:
            if text is None:
                self._icon.setVisible(True)
            else:
                self._checkIcon.setVisible(True)
            errorPos = (-1, -1)
        self.setText(error)
        self.setToolTip(fullError)
        if self._errorPos != errorPos:
            self._changeSignal.emit(*errorPos)
            self._errorPos = errorPos

    def getError(self, text):
        if text is None:
            return None, ''
        try:
            script = parser.parse(text)
        except UnexpectedInput as e:
            return (e.line - 1, e.column - 1), str(e)
        except LarkError as e:
            return (0, 0), e.args[0]
        issues = script.check()
        if issues:
            return (issues[0].line - 1, issues[0].column - 1), issues[0].message
        else:
            return None, 'No errors found in open script.'
