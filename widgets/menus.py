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
        self.aboutToShow.connect(self.onAboutToShow)

    def addAction(self, action):
        super().addAction(action)
        self._actions.append(action)

    def onAboutToShow(self):
        for action in self._actions:
            action.update()

    def relatesTo(self, obj):
        for action in self._actions:
            action.relatesTo(obj)

class ManageMenu(MyMenu):
    _text = 'Manage'
    _actions = [
        AddAccount, EditAccount, RemoveAccount, None,
        ReloadAccount, None,
        NewScript, OpenScript, DeleteScript, None,
        ActivateScript,
    ]
