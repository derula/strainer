from PyQt5.QtWidgets import QMenu, QToolBar

from ..actions import AddAccount, EditAccount, RemoveAccount, ReloadAccount, \
                      NewScript, RenameScript, DeleteScript, OpenScript, ActivateScript, \
                      SaveDocument, UndoEdit, RedoEdit, CutContent, CopyContent, \
                      PasteContent, DeleteContent, SelectAllContent, \
                      HomePage, PreviousPage, NextPage, ReloadPage, CopyUrl
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
    _actions = [
        SaveDocument, None, UndoEdit, RedoEdit, None, CutContent,
        CopyContent, PasteContent, DeleteContent, None, SelectAllContent
    ]


class NavigateMenu(MyMenu):
    _text = '&Navigate'
    _actions = [HomePage, None, PreviousPage, NextPage, ReloadPage, None, CopyUrl]


class MyToolBar(MyActionWidget, QToolBar):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName(self.__class__.__name__)


class ManageToolBar(MyToolBar):
    _text = 'Manage toolbar'
    _actions = [EditAccount, ReloadAccount, None, NewScript, RenameScript, None, OpenScript, ActivateScript]


class EditToolBar(MyToolBar):
    _text = 'Edit toolbar'
    _actions = [SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent]


class NavigateToolBar(MyToolBar):
    _text = 'Navigate toolbar'
    _actions = [HomePage, None, PreviousPage, NextPage, ReloadPage]
