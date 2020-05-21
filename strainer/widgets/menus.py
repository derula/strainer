from PyQt5.QtWidgets import QMenu

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

    def __init__(self, parent):
        super().__init__(parent, [])
        self.aboutToShow.connect(self.update)

    def update(self):
        self.clear()
        self._menu = self.parent().editor.createStandardContextMenu()
        for action in self._menu.actions():
            self.addAction(action)
