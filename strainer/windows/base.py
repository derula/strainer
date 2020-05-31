from abc import abstractmethod
from typing import Any, NamedTuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout
from qtawesome import icon

__all__ = ('DialogTitle', 'AddOrChangeDialog')


class DialogTitle(NamedTuple):
    icon: str
    text: str

class AddOrChangeDialog(QDialog):
    _addTitle: DialogTitle
    _changeTitle: DialogTitle
    _defaultValue: Any

    def __init__(self, parent):
        super().__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setLayout(QFormLayout())
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.layout().addRow(buttons)
        self._buttons = buttons.buttons()

    def setInputValid(self, value = True):
        self._buttons[0].setEnabled(value)

    def exec(self, oldValue = None):
        title = self._changeTitle if oldValue else self._addTitle
        self.setWindowIcon(icon(title.icon))
        self.setWindowTitle(title.text)
        self._setValue(oldValue or self._defaultValue)
        if super().exec() == QDialog.Accepted:
            return self._getValue()
        else:
            return None

    def _addField(self, caption, field):
        self.layout().insertRow(self.layout().rowCount() - 1, caption, field)

    @abstractmethod
    def _setValue(self, newValue):
        pass

    @abstractmethod
    def _getValue(self):
        pass
