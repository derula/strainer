from abc import abstractmethod
from PyQt5.QtWidgets import QAction
from qtawesome import icon

__all__ = ('MyAction', 'AccountAction', 'ScriptAction', 'NonEmptyAction')


class MyAction(QAction):
    _shortcut = None
    _icon = None
    _signal = None

    def __init__(self, tree):
        super().__init__(self._text, tree)
        if self._shortcut:
            self.setShortcut(self._shortcut)
        if self._icon:
            self.setIcon(icon(self._icon))
        self._defaultArgs = None
        if self._signal:
            self.triggered.connect(lambda checked: self.emit())

    def signal(self):
        return self._signal

    def setDefaultArgs(self, getArgs):
        self._defaultArgs = getArgs

    def connect(self, handler):
        (self._signal or self.triggered).connect(handler)

    def emit(self, *args):
        if self._defaultArgs:
            args += self._defaultArgs()[len(args):]
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
