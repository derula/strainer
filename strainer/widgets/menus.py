import string

from PyQt5.QtWidgets import QMenu
from qtawesome import icon

from .actions import *


class MyMenu(QMenu):
    def __init__(self, parent, all_actions):
        super().__init__(self._text, parent)
        self._actions = []
        for action in self.__class__._actions:
            if action:
                action = all_actions[action]
                self.addAction(action)
            else:
                self.addSeparator()

    def addAction(self, action):
        super().addAction(action)
        self._actions.append(action)

    @property
    def actions(self):
        return self._actions

    def update(self, item):
        for action in self._actions:
            action.update(item)

class ManageMenu(MyMenu):
    _text = 'Manage'
    _actions = [
        AddAccount, EditAccount, RemoveAccount, None,
        ReloadAccount, None,
        NewScript, OpenScript, DeleteScript, None,
        ActivateScript,
    ]

class EditMenu(MyMenu):
    _text = 'Edit'
    _actions = []
    _c_translate = bytes.maketrans(string.ascii_uppercase.encode('ascii'), string.ascii_lowercase.encode('ascii'))
    _c_delete = bytes(c for c in range(256) if chr(c) not in string.ascii_letters)
    _icons = {
        b'undo': 'mdi.undo', b'redo': 'mdi.redo', b'cut': 'mdi.content-cut', b'copy': 'mdi.content-copy',
        b'paste': 'mdi.content-paste', b'delete': 'mdi.delete', b'selectall': 'mdi.select-all'
    }

    def __init__(self, parent):
        super().__init__(parent, [])
        self.aboutToShow.connect(self.update)

    def update(self):
        self.clear()
        self._menu = self.parent().editor.createStandardContextMenu()
        for action in self._menu.actions():
            try:
                action.setIcon(icon(self._icons[action.text().encode('utf-8').translate(self._c_translate, self._c_delete)]))
            except KeyError:
                pass
            self.addAction(action)
