from abc import abstractmethod
from typing import Any, NamedTuple

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QMessageBox
from qtawesome import icon

__all__ = ('DialogTitle', 'ConfirmMessage', 'AddOrChangeDialog')


class DialogTitle(NamedTuple):
    icon: str
    text: str


class DialogTitleMixin:
    def _applyTitle(self, title):
        self.setWindowIcon(icon(title.icon))
        self.setWindowTitle(title.text)


class ConfirmMessage(DialogTitleMixin, QMessageBox):
    _title: DialogTitle
    _textTemplate: str
    _acceptText: str
    _rejectText: str

    def __init__(self, parent):
        super().__init__(parent)
        self._applyTitle(self._title)
        self.setIcon(QMessageBox.Question)
        self._confirm = self.addButton(self._acceptText, QMessageBox.DestructiveRole)
        self.addButton(self._rejectText, QMessageBox.RejectRole)

    def exec(self, *args, **kwargs):
        self.setText(self._textTemplate.format(*args, **kwargs))
        self._confirm.setFocus()
        super().exec()
        return self.clickedButton() == self._confirm


class AddOrChangeDialog(DialogTitleMixin, QDialog):
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
        self._illegalNames = None

    def setInputValid(self, value=True):
        self._buttons[0].setEnabled(value)

    def isNameLegal(self, newName):
        return newName not in self._illegalNames

    def exec(self, illegalNames, oldValue=None):
        self._illegalNames = illegalNames
        self._applyTitle(self._changeTitle if oldValue else self._addTitle)
        self._setValue(oldValue or self._defaultValue)
        if super().exec() == QDialog.Accepted:
            return self._getValue()
        else:
            return None

    def _addField(self, caption, field):
        self.layout().insertRow(self.layout().rowCount() - 1, caption, field)
        return field

    def _getField(self, index):
        return self.layout().itemAt(index, QFormLayout.FieldRole).widget()

    @abstractmethod
    def _setValue(self, newValue):
        pass

    @abstractmethod
    def _getValue(self):
        pass
