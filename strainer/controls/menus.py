import string

from PyQt5.QtWidgets import QMenu
from qtawesome import icon

from ..actions import *
from .base import MyActionWidget


class MyMenu(MyActionWidget, QMenu):
    def update(self, obj=None):
        for action in self.actions():
            try:
                action.update(obj)
            except AttributeError:
                pass

class AccountMenu(MyMenu):
    _text = 'Account'
    _actions = [AddAccount, EditAccount, RemoveAccount, None, ReloadAccount]


class ScriptMenu(MyMenu):
    _text = 'Script'
    _actions = [NewScript, RenameScript, DeleteScript, None, OpenScript, ActivateScript]


class DocumentMenu(MyMenu):
    _text = 'Document'
    _actions = [SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent, DeleteContent, None, SelectAllContent]
