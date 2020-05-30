from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize

from ..sieve import SieveLexer
from ..sieve.lexer import TagStyle


class Editor(QsciScintilla):
    def __init__(self, parent):
        super().__init__(parent)
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
