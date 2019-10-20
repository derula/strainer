from PyQt5.QtWidgets import QMenu

from .actions import *


class ManageMenu(QMenu):
    ACCOUNT_ACTIONS = [AddAccount, EditAccount, RemoveAccount]
    SCRIPT_ACTIONS = [NewScript, ToggleScript, DeleteScript]

    def __init__(self, parent):
        super().__init__('Manage', parent)
        self.actions = {}
        for cls in self.ACCOUNT_ACTIONS:
            action = self.actions[cls] = cls(parent)
            self.addAction(action)
        self.addSeparator()
        for cls in self.SCRIPT_ACTIONS:
            action = self.actions[cls] = cls(parent)
            self.addAction(action)
        self.aboutToShow.connect(self.onAboutToShow)

    def onAboutToShow(self):
        for action in self.actions.values():
            action.update()
