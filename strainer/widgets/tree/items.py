from PyQt5.QtCore import Qt
from qtawesome import icon

from ...types import Account
from .base import TreeItem, TreeItemStatus


class AccountItem(TreeItem):
    def __init__(self, value):
        super().__init__(['', ''])
        self.value = value
        self._activeScript = None
        self.setIcon(0, icon('mdi.account'))

    @property
    def value(self):
        return Account(self.name, *self.data(0, Qt.UserRole))

    @value.setter
    def value(self, value):
        self.name, *value = value
        self.setData(0, Qt.UserRole, value)

    def activeScript(self):
        return self._activeScript

    def setActiveScript(self, script):
        if self._activeScript:
            self._activeScript.active = False
            self._activeScript = None
        if script:
            self._activeScript = script
            self._activeScript.active = True

    def addScriptItem(self, scriptName):
        newItem = ScriptItem(scriptName)
        self.addChild(newItem)
        self.sortChildren(0, Qt.AscendingOrder)
        return newItem

    def replaceScriptItems(self, activeScript, inactiveScripts):
        self.takeChildren()
        if activeScript:
            self._activeScript = ScriptItem(activeScript, True)
            self.addChild(self._activeScript)
        else:
            self._activeScript = None
        self.addChildren(ScriptItem(script) for script in inactiveScripts)
        self.sortChildren(0, Qt.AscendingOrder)
        self.setExpanded(True)

class ScriptItem(TreeItem):
    def __init__(self, value, is_active=False):
        self._open = False
        self._active = is_active
        super().__init__([value, ''])
        self.setIcon(0, icon('mdi.file'))

    def setStatus(self, status, tooltip=''):
        super().setStatus(status, tooltip)
        self._applyState()

    @property
    def active(self):
        return self._active

    @active.setter
    def active(self, value):
        self._active = value
        self._applyState()

    @property
    def open(self):
        return self._open

    @open.setter
    def open(self, value):
        self._open = value
        self._applyState()

    def _applyState(self):
        font = self.font(0)
        font.setItalic(self._open)
        self.setFont(0, font)
        if self._status == TreeItemStatus.Normal:
            if self.active:
                self.setIcon(1, icon('mdi.check-bold'))
            else:
                self.setIcon(1, icon())
