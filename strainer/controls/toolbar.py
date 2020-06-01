from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar
import qtawesome as qta

from ..actions import *
from .base import MyActionWidget


class MyToolBar(MyActionWidget, QToolBar):
    pass

class ManageToolbar(MyToolBar):
    _actions = [EditAccount, ReloadAccount, None, NewScript, RenameScript, None, OpenScript, ActivateScript]

class EditToolbar(MyToolBar):
    _actions = [SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent]

class DocumentToolbar(MyToolBar):
    _actions = [
        SaveDocument, None, UndoEdit, RedoEdit, None, CutContent, CopyContent, PasteContent,
    ]
