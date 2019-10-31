from abc import ABC
from PyQt5.QtWidgets import QAction, QActionGroup

__all__ = ('AddAccount', 'EditAccount', 'RemoveAccount', 'ReloadAccount', 'NewScript', 'ToggleScript', 'DeleteScript')


class MyAction(QAction):
    def __init__(self, tree):
        super().__init__(self._text, tree)
        self._related = None

    def update(self):
        self.setEnabled(self._shouldEnable())

    def relatesTo(self, obj):
        self._related = obj

    def _shouldEnable(self):
        return not self._related.signalsBlocked()

class AccountAction(MyAction):
    def _shouldEnable(self):
        try:
            return super()._shouldEnable() and self._related.currentItem().parent() is None
        except AttributeError:
            return False

class ScriptAction(MyAction):
    def _shouldEnable(self):
        try:
            return super()._shouldEnable() and self._related.currentItem().parent() is not None
        except AttributeError:
            return False

class NonEmptyAction(MyAction):
    def _shouldEnable(self):
        return super()._shouldEnable() and self._related.currentItem() is not None

class AddAccount(MyAction):
    _text = 'Add account'

class EditAccount(AccountAction):
    _text = 'Account settings'

class RemoveAccount(AccountAction):
    _text = 'Remove account'

class ReloadAccount(NonEmptyAction):
    _text = 'Reload account'

class NewScript(NonEmptyAction):
    _text = 'New script'

class ToggleScript(ScriptAction):
    _text = 'Activate script'

class DeleteScript(ScriptAction):
    _text = 'Delete script'
