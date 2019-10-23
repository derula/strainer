from abc import ABC
from PyQt5.QtWidgets import QAction, QActionGroup

__all__ = ('AddAccount', 'EditAccount', 'RemoveAccount', 'NewScript', 'ToggleScript', 'DeleteScript')


class MyAction(QAction):
    def __init__(self, tree):
        super().__init__(self._text, tree)
        self._related = None

    def update(self):
        pass

    def relatesTo(self, obj):
        self._related = obj

class AccountAction:
    def update(self):
        try:
            enabled = self._related.currentItem().parent() is None
        except AttributeError:
            enabled = False
        self.setEnabled(enabled)


class ScriptAction:
    def update(self):
        try:
            enabled = self._related.currentItem().parent() is not None
        except AttributeError:
            enabled = False
        self.setEnabled(enabled)

class AddAccount(MyAction):
    _text = 'Add account'

class EditAccount(AccountAction, MyAction):
    _text = 'Account settings'

class RemoveAccount(AccountAction, MyAction):
    _text = 'Remove account'

class NewScript(MyAction):
    _text = 'New script'

    def update(self):
        self.setEnabled(self._related.currentItem() is not None)

class ToggleScript(ScriptAction, MyAction):
    _text = 'Activate script'

class DeleteScript(ScriptAction, MyAction):
    _text = 'Delete script'
