from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QToolButton, QLineEdit, QSizePolicy, QWidget
from qtawesome import icon

from ..types import FindOptions, FindQuery


class FindBar(QWidget):
    findFirst = pyqtSignal(FindQuery)
    findNext = pyqtSignal()
    cancelFind = pyqtSignal()
    __regExToggles = {'caseSensitive', 'wholeWords'}
    __optSettings = {
        'caseSensitive': ['mdi.format-letter-case', 'Enable case-sensitive search.'],
        'wholeWords': ['mdi.format-letter-matches', 'Only match whole words.'],
        'regularExpression': ['mdi.regex', 'Search by regular expression.'],
        'inSelection': ['mdi.selection-search', 'Only search within current selection.'],
    }

    def __init__(self, parent, options: FindOptions):
        super().__init__(parent)
        self._expression = QLineEdit(self)
        self._expression.setClearButtonEnabled(True)
        self._expression.returnPressed.connect(self.onReturnPressed)
        self._expression.textChanged.connect(self._clearErrorState)
        self._options = {}
        self.setLayout(QHBoxLayout())
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().addWidget(QLabel('Find:'))
        self.layout().addWidget(self._expression)
        for option in options._fields:
            if not getattr(options, option):
                continue
            ico, tip = self.__optSettings[option]
            btn = QToolButton(self, autoRaise=True, checkable=True, icon=icon(ico), statusTip=tip)
            if option == 'regularExpression':
                btn.toggled.connect(self.onRegExToggle)
            else:
                btn.toggled.connect(self.onOptionToggle)
            self._options[option] = btn
            self.layout().addWidget(btn)
        closeBtn = QToolButton(self, autoRaise=True, icon=icon('mdi.close'), statusTip='Cancel search and hide this panel.')
        closeBtn.clicked.connect(self.hide)
        self.layout().addWidget(closeBtn)
        self._optsChanged = None
        self.setVisible(False)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()

    def show(self, expr):
        expr = expr or ''
        if 'inSelection' in self._options:
            multiline = '\n' in expr
            self._options['inSelection'].setChecked(multiline)
            if multiline:
                expr = ''
        self._expression.setText(expr)
        if expr and 'regularExpression' in self._options:
            self._options['regularExpression'].setChecked(False)
        self._optsChanged = True
        self._clearErrorState()
        self.setVisible(True)
        self._expression.setFocus(Qt.PopupFocusReason)

    def hide(self):
        self.setVisible(False)
        self.cancelFind.emit()

    def query(self):
        kwargs = {key: option.isChecked() for key, option in self._options.items()}
        if kwargs.get('regularExpression'):
            for option in kwargs.keys() & self.__regExToggles:
                del kwargs[option]
        return FindQuery(self._expression.text(), FindOptions(**kwargs), callback=self.onFind)

    def onOptionToggle(self, checked):
        self._optsChanged = True
        self.onFind()

    def onRegExToggle(self, checked):
        self.onOptionToggle(checked)
        for option in self._options.keys() & self.__regExToggles:
            self._options[option].setEnabled(not checked)

    def onReturnPressed(self):
        if self._optsChanged or self._expression.isModified():
            self.findFirst.emit(self.query())
            self._expression.setModified(False)
            self._optsChanged = False
        else:
            self.findNext.emit()

    def onFind(self, found=True):
        if not found:
            self.window().statusBar().showMessage('No results found.', 1500)
            palette = QPalette()
            col = palette.color(QPalette.Base)
            palette.setColor(QPalette.Base, QColor((col.red() + 255) / 2, col.green() / 2, col.blue() / 2))
            self._expression.setPalette(palette)

    def _clearErrorState(self):
        self._expression.setPalette(QPalette())
