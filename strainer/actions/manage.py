from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QTreeWidgetItem

from .base import *


class AddAccount(MyAction):
    _text = '&Add account'
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Insert)
    _icon = 'mdi.account-plus'

    def _shouldEnable(self, item):
        return item is not None

class SaveScript(MyAction):
    _text = '&Save'
    _shortcut = QKeySequence(Qt.CTRL | Qt.Key_S)
    _icon = 'mdi.file-upload'
    _signal = pyqtSignal(QTreeWidgetItem)

class EditAccount(NonEmptyAction):
    _text = 'Account &settings'
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Return)
    _icon = 'mdi.account-edit'
    _signal = pyqtSignal(QTreeWidgetItem)

class RemoveAccount(NonEmptyAction):
    _text = '&Remove account'
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Delete)
    _icon = 'mdi.account-remove'
    _signal = pyqtSignal(QTreeWidgetItem)

class ReloadAccount(NonEmptyAction):
    _text = 'Re&load account'
    _shortcut = QKeySequence(Qt.Key_F5)
    _icon = 'mdi.account-convert'
    _signal = pyqtSignal(QTreeWidgetItem)

class NewScript(NonEmptyAction):
    _text = '&New script'
    _shortcut = QKeySequence(Qt.Key_Insert)
    _icon = 'mdi.file-plus'
    _signal = pyqtSignal(QTreeWidgetItem)

class RenameScript(ScriptAction):
    _text = '&Rename script'
    _shortcut = QKeySequence(Qt.Key_F2)
    _icon = 'mdi.file-edit'
    _signal = pyqtSignal(QTreeWidgetItem)

class DeleteScript(ScriptAction):
    _text = '&Delete script'
    _shortcut = QKeySequence(Qt.Key_Delete)
    _icon = 'mdi.file-remove'
    _signal = pyqtSignal(QTreeWidgetItem)

class OpenScript(ScriptAction):
    _text = '&Open script'
    _shortcut = QKeySequence(Qt.Key_Return)
    _icon = 'mdi.file-download'
    _signal = pyqtSignal(QTreeWidgetItem)

    def _shouldEnable(self, item):
        return super()._shouldEnable(item) and not item.open

class ActivateScript(MyStatefulAction):
    _texts = ('&Activate script', 'De&activate script')
    _icons = ('mdi.file-check', 'mdi.file')
    _signal = pyqtSignal(QTreeWidgetItem)

    def _getState(self, item):
        return item and item.parent() and item.active
