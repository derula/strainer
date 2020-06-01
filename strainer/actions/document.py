from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QApplication

from .base import *


class SaveDocument(EditorAction):
    _text = '&Save'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_S)
    _icon = 'mdi.file-upload'

    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.isModified()

class UndoEdit(EditorAction):
    _text = '&Undo'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_Z)
    _icon = 'mdi.undo'

    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.isUndoAvailable()

class RedoEdit(EditorAction):
    _text = '&Redo'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_Y)
    _icon = 'mdi.redo'

    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.isRedoAvailable()

class CutContent(SelectionAction):
    _text = 'Cu&t'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_X)
    _icon = 'mdi.content-cut'

class CopyContent(SelectionAction):
    _text = '&Copy'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_C)
    _icon = 'mdi.content-copy'

class PasteContent(EditorAction):
    _text = '&Paste'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_V)
    _icon = 'mdi.content-paste'

    # The dataChanged signal doesn't seem to be working for me,
    # so this made the paste button get stuck in disabled until
    # the document is manipulated...
    #def _shouldEnable(self, editor):
    #    return super()._shouldEnable(editor) and QApplication.clipboard().text() != ''

class DeleteContent(SelectionAction):
    _text = '&Delete'
    _shortcut = QKeySequence(Qt.Key_Delete)
    _icon = 'mdi.delete'

class SelectAllContent(EditorAction):
    _text = 'Select &all'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_A)
    _icon = 'mdi.select-all'
