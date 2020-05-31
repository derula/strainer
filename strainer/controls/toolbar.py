from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolBar
import qtawesome as qta

from ..actions import *
from .base import MyActionWidget


class Toolbar(MyActionWidget, QToolBar):
    _actions = [
        EditAccount, ReloadAccount, None, NewScript, RenameScript, None, OpenScript, SaveScript, ActivateScript,
    ]
