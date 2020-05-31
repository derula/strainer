from PyQt5.QtWidgets import QFormLayout

from .base import *
from ..controls import *


class AccountDialog(AddOrChangeDialog):
    _addTitle = DialogTitle('mdi.account-plus', 'Add new account')
    _changeTitle = DialogTitle('mdi.account-edit', 'Change account settings')
    _defaultValue = ('New account', '', 4190, '', '', False, None)

    def __init__(self, parent):
        super().__init__(parent)
        self._addField('Display name:', StringField())
        self._addField('Server address:', StringField())
        self._addField('Server port:', IntegerField())
        self._addField('User name:', StringField())
        self._addField('Password:', PasswordField())
        self._addField('Use STARTTLS:', CheckboxField('enable'))
        self._addField('Authentication:', OptionsField([
            ('Automatic', None),
            ('Digest MD5', 'DIGEST-MD5'),
            ('Plain', 'PLAIN'),
            ('Login', 'LOGIN'),
        ]))

    def _setValue(self, values):
        layout = self.layout()
        for i, value in enumerate(values):
            layout.itemAt(i, QFormLayout.FieldRole).widget().setValue(value)
        layout.itemAt(0, QFormLayout.FieldRole).widget().setFocus()

    def _getValue(self):
        layout = self.layout()
        return [layout.itemAt(i, QFormLayout.FieldRole).widget().getValue() for i in range(layout.rowCount() - 1)]

class ScriptNameDialog(AddOrChangeDialog):
    _addTitle = DialogTitle('mdi.file-plus', 'Add new script')
    _changeTitle = DialogTitle('mdi.file-edit', 'Rename script')
    _defaultValue = ''

    def __init__(self, parent):
        super().__init__(parent)
        field = StringField(128)
        field.textChanged.connect(self.onTextChanged)
        self._getValue = field.getValue
        self._addField('New script name:', field)
        self._illegalValues = None

    def exec(self, account, oldValue = None):
        self._illegalValues = account.scriptNames()
        return super().exec(oldValue)

    def _setValue(self, newValue):
        field = self.layout().itemAt(0, QFormLayout.FieldRole).widget()
        field.setValue(newValue)
        field.setFocus()
        self.onTextChanged(newValue)

    def onTextChanged(self, newText):
        self.setInputValid(bool(newText) and newText not in self._illegalValues)
