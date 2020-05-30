from abc import abstractmethod
from PyQt5.QtWidgets import QAction
from qtawesome import icon

from ..widgets.tree_items import AccountItem, ScriptItem

__all__ = ('MyAction', 'AccountAction', 'ScriptAction', 'NonEmptyAction')


class MyAction(QAction):
    _shortcut = None
    _icon = None

    def __init__(self, tree):
        super().__init__(self._text, tree)
        if self._shortcut:
            self.setShortcut(self._shortcut)
        if self._icon:
            self.setIcon(icon(self._icon))
        name = self.__class__.__name__
        self._signalName = f'{name[0].lower()}{name[1:]}'
        self._signal = self._signalArgs = None
        self.triggered.connect(self.emit)

    def signal(self, owner):
        self._signal = getattr(owner, self._signalName)
        return self._signal

    def signalArgs(self, getArgs):
        self._signalArgs = getArgs

    def connect(self, receiver):
        self._signal.connect(getattr(receiver, self._signalName))

    def emit(self):
        if self._signal is not None:
            args = self._signalArgs() if self._signalArgs is not None else ()
            self._signal.emit(*args)

    def update(self, target):
        self.setEnabled(self._shouldEnable(target))

    @abstractmethod
    def _shouldEnable(self, target):
        pass

class AccountAction(MyAction):
    def _shouldEnable(self, item):
        try:
            return isinstance(item, AccountItem)
        except AttributeError:
            return False

class ScriptAction(MyAction):
    def _shouldEnable(self, item):
        try:
            return isinstance(item, ScriptItem)
        except AttributeError:
            return False

class NonEmptyAction(MyAction):
    def _shouldEnable(self, item):
        return bool(item)
