from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from .base import *


class AddAccount(MyAction):
    _text = 'Add account'
    _shortcut = QKeySequence(Qt.Key_Insert)
    _icon = 'mdi.account-plus'

    def _shouldEnable(self, item):
        return item is not None

class EditAccount(AccountAction):
    _text = 'Account settings'
    _shortcut = QKeySequence(Qt.Key_Return)
    _icon = 'mdi.account-edit'

class RemoveAccount(AccountAction):
    _text = 'Remove account'
    _shortcut = QKeySequence(Qt.Key_Delete)
    _icon = 'mdi.account-remove'

class ReloadAccount(NonEmptyAction):
    _text = 'Reload account'
    _shortcut = QKeySequence(Qt.Key_F5)
    _icon = 'mdi.account-convert'

class NewScript(NonEmptyAction):
    _text = 'New script'
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Insert)
    _icon = 'mdi.file-plus'

class OpenScript(ScriptAction):
    _text = 'Open script'
    _shortcut = QKeySequence(Qt.Key_Return)
    _icon = 'mdi.file-download'

class DeleteScript(ScriptAction):
    _text = 'Delete script'
    _shortcut = QKeySequence(Qt.Key_Delete)
    _icon = 'mdi.file-remove'

class ActivateScript(ScriptAction):
    _text = 'Activate script'
    _icon = 'mdi.file-check'

    def _shouldEnable(self, item):
        return super()._shouldEnable(item) and not item.active
