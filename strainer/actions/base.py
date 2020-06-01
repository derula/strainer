from abc import abstractmethod
from PyQt5.QtWidgets import QAction
from qtawesome import icon

__all__ = (
    'MyAction', 'MyStatefulAction',
    'AccountAction', 'ScriptAction', 'NonEmptyAction',
    'EditorAction', 'SelectionAction',
)


class MyAction(QAction):
    _info = None
    _icon = None
    _signal = None
    _shortcut = None

    def __init__(self, parent):
        super().__init__(parent)
        self.setState()
        if self._shortcut:
            self.setShortcut(self._shortcut)
        self._defaultArgs = None
        if self._signal:
            super().triggered.connect(lambda checked: self.trigger())

    def setState(self, state=None):
        self.setText(self._text)
        if self._icon:
            self.setIcon(icon(self._icon))
        if self._info:
            self.setStatusTip(self._info)

    def setDefaultArgs(self, getArgs):
        self._defaultArgs = getArgs

    @property
    def triggered(self):
        return self._signal or super().triggered

    def trigger(self, *args):
        if not self._signal:
            return super().trigger()
        if self._defaultArgs:
            args += self._defaultArgs()[len(args):]
        self._signal.emit(*args)

    def update(self, target):
        self.setEnabled(self._shouldEnable(target))

    @abstractmethod
    def _shouldEnable(self, target):
        pass

class MyStatefulAction(MyAction):
    _texts = ()
    _infos = ()
    _icons = ()

    def setState(self, state=None):
        self._state = state
        super().setState(state)

    @property
    def _text(self):
        return self._texts[self._state or 0]

    @property
    def _info(self):
        try:
            return self._infos[self._state or 0]
        except IndexError:
            return None

    @property
    def _icon(self):
        try:
            return self._icons[self._state or 0]
        except IndexError:
            return None

    def update(self, target):
        self.setState(self._getState(target))
        super().update(target)

    def _shouldEnable(self, target):
        return self._state is not None

    @abstractmethod
    def _getState(self, target):
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

class EditorAction(MyAction):
    def _shouldEnable(self, editor):
        return not editor.isReadOnly()

class SelectionAction(EditorAction):
    def _shouldEnable(self, editor):
        return super()._shouldEnable(editor) and editor.hasSelectedText()
