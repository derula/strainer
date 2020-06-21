from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from .base import EditorAction, SelectionAction


class SaveDocument(EditorAction):
    _text = '&Save'
    _info = "Save changes made to this script's content."
    _icon = 'mdi.file-upload'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_S)

    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.isModified()


class UndoEdit(EditorAction):
    _text = '&Undo'
    _info = "Undo the last change made to this script's content."
    _icon = 'mdi.undo'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_Z)

    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.isUndoAvailable()


class RedoEdit(EditorAction):
    _text = '&Redo'
    _info = "Redo the most recently undone change to this script's content."
    _icon = 'mdi.redo'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_Y)

    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.isRedoAvailable()


class CutContent(SelectionAction):
    _text = 'Cu&t'
    _info = "Move the selected part of this script's content to the clipboard."
    _icon = 'mdi.content-cut'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_X)


class CopyContent(SelectionAction):
    _text = '&Copy'
    _info = "Copy the selected part of this script's content to the clipboard."
    _icon = 'mdi.content-copy'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_C)


class PasteContent(EditorAction):
    _text = '&Paste'
    _info = "Insert text from the clipboard at the current cursor position."
    _icon = 'mdi.content-paste'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_V)

    # The dataChanged signal doesn't seem to be working for me,
    # so this made the paste button get stuck in disabled until
    # the document is manipulated...
    # def _shouldEnable(self, editor):
    #     return super()._shouldEnable(editor) and QApplication.clipboard().text() != ''


class DeleteContent(SelectionAction):
    _text = '&Delete'
    _info = 'Delete the currently selected content from this script.'
    _icon = 'mdi.delete'
    _shortcut = QKeySequence(Qt.Key_Delete)


class SelectAllContent(EditorAction):
    _text = 'Select &all'
    _info = "Select this script's entire content."
    _icon = 'mdi.select-all'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_A)
