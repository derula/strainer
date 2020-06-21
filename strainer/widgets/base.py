from dataclasses import dataclass, field

__all__ = ('Menu', 'MenuMixin')


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
