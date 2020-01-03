from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize

from ..sieve import SieveLexer


class Editor(QsciScintilla):
    def __init__(self, reference):
        super().__init__()
        self._reference = reference

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
        for style, value in self.lexer().scan(position):
            self._reference.browse(style.name.lower(), value.decode('ascii').lower())
            break

    def sizeHint(self):
        return QSize(750, 600)
