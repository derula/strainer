from PyQt5.QtWidgets import QVBoxLayout, QWidget
from dataclasses import dataclass, field

from ..controls import FindBar
from ..types import FindOptions, FindQuery

__all__ = ('Menu', 'MenuMixin', 'Find', 'FindMixin')


@dataclass(frozen=True)
class Menu:
    type: type
    actions: dict = field(default_factory=dict)
    updateSignals: tuple = ()


class MenuMixin:
    _menu: Menu

    def __init__(self, parent):
        super().__init__(parent)
        menu = self._menu.type(self.window())
        for action, reaction in self._menu.actions.items():
            self.window().action(action).triggered.connect(getattr(self, reaction))
        for signal in self._menu.updateSignals:
            getattr(self, signal).connect(self.updateMenu)
        self._menu = menu

    def contextMenuEvent(self, event):
        self.updateMenu()
        self._menu.popup(event.globalPos())

    def updateMenu(self):
        self._menu.update(self)


@dataclass(frozen=True)
class Find:
    action: type
    options: FindOptions


class FindMixin:
    _find: Find

    def __init__(self, parent):
        super().__init__(parent.window())
        findBar = FindBar(parent.window(), self._find.options)
        widget = QWidget(parent)
        widget.setLayout(QVBoxLayout())
        widget.layout().setContentsMargins(0, 0, 0, 0)
        widget.layout().addWidget(findBar)
        widget.layout().addWidget(self)
        findBar.findFirst.connect(self.findFirst)
        findBar.findNext.connect(self.findNext)
        findBar.cancelFind.connect(self.cancelFind)
        self.window().action(self._find.action).triggered.connect(lambda: findBar.show(self.selectedText()))
        self._find = None

    def canFindNext(self):
        return self._find is not None

    def findFirst(self, query: FindQuery):
        if not self.canFindNext():
            self.cancelFind()
        self._find = query
        self._findFirst(query)

    def findNext(self):
        if not self.canFindNext():
            raise RuntimeError('Cannot findNext before findFirst.')
        self._findNext(self._find)

    def cancelFind(self):
        self._find = None
        self._cancelFind()

    def _findFirst(self, query: FindQuery):
        self._findNext(query)

    def _findNext(self, query: FindQuery):
        raise NotImplementedError('Abstract method _findNext must be implemented by all subclasses.')

    def _cancelFind(self):
        raise NotImplementedError('Abstract method _findNext must be implemented by all subclasses.')
