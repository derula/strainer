from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtWidgets import QApplication

from ...actions import *
from ...controls import EditMenu
from .lexer import SieveLexer
from .styles import TagStyle


class Editor(QsciScintilla):
    _actions = {
        UndoEdit: 'undo', RedoEdit: 'redo',
        CutContent: 'cut', CopyContent: 'copy', PasteContent: 'paste',
        DeleteContent: 'removeSelectedText', SelectAllContent: 'selectAll',
    }

    def __init__(self, parent):
        super().__init__(parent)
        self._menu = EditMenu(self.window())
        for action, reaction in self._actions.items():
            self.window().action(action).triggered.connect(getattr(self, reaction))
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
        self.selectionChanged.connect(self.onChanged)
        self.textChanged.connect(self.onChanged)
        #QApplication.clipboard().dataChanged.connect(onChanged)  # doesn't seem to be working...?

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

    def onChanged(self):
        self._menu.update(self)

    def sizeHint(self):
        return QSize(750, 600)

    def contextMenuEvent(self, event):
        self._menu.popup(event.globalPos())

    def selectAll(self):
        super().selectAll(True)

    def open(self, text):
        self.setText(text)
        self.setReadOnly(False)
        self.setFocus(Qt.OtherFocusReason)
        self.setModified(False)
        self.onChanged()

    def close(self):
        self.setText('')
        self.setReadOnly(True)
        self.setModified(False)
        self.onChanged()
