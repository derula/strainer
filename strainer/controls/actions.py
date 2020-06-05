from PyQt5.QtWidgets import QMenu, QToolBar

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
    _text = '&Account'
    _actions = [AddAccount, EditAccount, RemoveAccount, None, ReloadAccount]

class ScriptMenu(MyMenu):
    _text = '&Script'
    _actions = [NewScript, RenameScript, DeleteScript, None, OpenScript, ActivateScript]

class ManageMenu(MyMenu):
    _text = '&Manage'
    _actions = [*AccountMenu._actions, None, *ScriptMenu._actions]

class EditMenu(MyMenu):
    _text = '&Edit'
    _actions = [SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent, DeleteContent, None, SelectAllContent]

class NavigateMenu(MyMenu):
    _text = '&Navigate'
    _actions = [HomePage, None, PreviousPage, NextPage, ReloadPage, None, CopyUrl]

class MyToolBar(MyActionWidget, QToolBar):
    pass

class ManageToolBar(MyToolBar):
    _actions = [EditAccount, ReloadAccount, None, NewScript, RenameScript, None, OpenScript, ActivateScript]

class EditToolBar(MyToolBar):
    _actions = [SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent]

class NavigateToolBar(MyToolBar):
    _actions = [HomePage, None, PreviousPage, NextPage, ReloadPage]
