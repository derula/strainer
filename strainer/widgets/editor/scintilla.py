from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

from ...actions import *
from ...controls import EditMenu
from ..base import *
from .lexer import SieveLexer
from .styles import TagStyle


class Editor(MenuMixin, QsciScintilla):
    _menu = Menu(
        EditMenu,
        {
            UndoEdit: 'undo', RedoEdit: 'redo',
            CutContent: 'cut', CopyContent: 'copy', PasteContent: 'paste',
            DeleteContent: 'removeSelectedText', SelectAllContent: 'selectAll',
        },
        ('selectionChanged', 'textChanged')
    )

    def __init__(self, parent):
        super().__init__(parent)
        self.close()

        self.setMinimumSize(QSize(300, 200))
        self.setScrollWidth(300)
        self.setScrollWidthTracking(True)

        self.setUtf8(True)
        self.setEolMode(QsciScintilla.EolWindows)

        self.setMarginLineNumbers(0, True)
        self.linesChanged.connect(lambda: self.setMarginWidth(0, f'0{self.lines()}'))

        self.setAutoIndent(True)
        self.setTabWidth(2)
        self.setTabIndents(True)
        self.setBackspaceUnindents(True)
        self.setIndentationsUseTabs(False)
        self.setIndentationGuides(True)

        self.setBraceMatching(QsciScintilla.BraceMatch.SloppyBraceMatch)

        self.setLexer(SieveLexer(self))
        self.SCN_HOTSPOTCLICK.connect(self.onHotspotClicked)
        #QApplication.clipboard().dataChanged.connect(updateMenu)  # doesn't seem to be working...?

        self.indicatorDefine(QsciScintilla.IndicatorStyle.DotsIndicator, 0)
        self.setIndicatorForegroundColor(QColor('red'), 0)
        self.indicatorDefine(QsciScintilla.IndicatorStyle.TriangleCharacterIndicator, 1)
        self.setIndicatorForegroundColor(QColor('red'), 1)

    def onHotspotClicked(self, position, modifiers):
        position = self.SendScintilla(QsciScintilla.SCI_WORDSTARTPOSITION, position, True)
        if self.text(position - 1, position) == ':':
            position -= 1
        for style, value in self.lexer().scan(position):
            category = style.name.lower()
            if isinstance(style, TagStyle):
                page, category = category, 'operators'
            else:
                page = value.decode('ascii').lower()
            self.window().reference().browse(category, page)
            break

    def sizeHint(self):
        return QSize(750, 600)

    def open(self, text):
        self.setText(text)
        self.setReadOnly(False)
        self.setFocus(Qt.OtherFocusReason)
        self.setModified(False)
        self.updateMenu()

    def selectAll(self):
        super().selectAll(True)

    def setParseError(self, line, col, length=1):
        self.SendScintilla(QsciScintilla.SCI_SETINDICATORCURRENT, 1)
        self.SendScintilla(QsciScintilla.SCI_INDICATORCLEARRANGE, 0, self.length())
        if line >= 0 and col >= 0:
            start = self.positionFromLineIndex(line, col) - length
            self.SendScintilla(QsciScintilla.SCI_INDICATORFILLRANGE, start, length)

    def close(self):
        self.setText('')
        self.setReadOnly(True)
        self.setModified(False)
        self.updateMenu()
