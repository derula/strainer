from abc import abstractmethod
from PyQt5.QtWidgets import QAction
from qtawesome import icon

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
        return bool(item and not item.parent())

class ScriptAction(MyAction):
    def _shouldEnable(self, item):
        return bool(item and item.parent())

class NonEmptyAction(MyAction):
    def _shouldEnable(self, item):
        return bool(item)
