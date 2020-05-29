from abc import ABC, abstractmethod
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction, QActionGroup
from qtawesome import icon

from .tree import AccountItem, ScriptItem

__all__ = (
    'AddAccount', 'EditAccount', 'RemoveAccount', 'ReloadAccount',
    'NewScript', 'OpenScript', 'DeleteScript', 'ActivateScript',
)


class MyAction(QAction):
    _shortcut = None
    _icon = None

    def __init__(self, tree):
        super().__init__(self._text, tree)
        if self._shortcut:
            self.setShortcut(self._shortcut)
        if self._icon:
            self.setIcon(icon(self._icon))

    def update(self, target):
        self.setEnabled(self._shouldEnable(target))

    @abstractmethod
    def _shouldEnable(self, target):
        pass

class AccountAction(MyAction):
    def _shouldEnable(self, item):
        try:
            return isinstance(item, AccountItem)
        except AttributeError:
            return False

class ScriptAction(MyAction):
    def _shouldEnable(self, item):
        try:
            return isinstance(item, ScriptItem)
        except AttributeError:
            return False

class NonEmptyAction(MyAction):
    def _shouldEnable(self, item):
        return bool(item)

class AddAccount(MyAction):
    _text = 'Add account'
    _shortcut = QKeySequence(Qt.Key_Insert)
    _icon = 'mdi.account-plus'

    def _shouldEnable(self, item):
        return item is not False

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
