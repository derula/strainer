from PyQt5.QtWidgets import QFormLayout

from .base import AddOrChangeDialog, DialogTitle
from ..controls import StringField, IntegerField, PasswordField, CheckboxField, OptionsField


class AccountDialog(AddOrChangeDialog):
    _addTitle = DialogTitle('mdi.account-plus', 'Add new account')
    _changeTitle = DialogTitle('mdi.account-edit', 'Change account settings')
    _defaultValue = ('New account', '', 4190, '', '', False, None)

    def __init__(self, parent):
        super().__init__(parent)
        self._addField('Display name:', StringField()).textChanged.connect(self.onTextChanged)
        self._addField('Server address:', StringField()).textChanged.connect(self.onTextChanged)
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
        for i, value in enumerate(values):
            self._getField(i).setValue(value)
        self._getField(0).setFocus()

    def _getValue(self):
        return [self._getField(i).getValue() for i in range(self.layout().rowCount() - 1)]

    def onTextChanged(self, _):
        name = self._getField(0).getValue()
        address = self._getField(1).getValue()
        self.setInputValid(self.isNameLegal(name) and bool(address))


class ScriptNameDialog(AddOrChangeDialog):
    _addTitle = DialogTitle('mdi.file-plus', 'Add new script')
    _changeTitle = DialogTitle('mdi.file-edit', 'Rename script')
    _defaultValue = ''

    def __init__(self, parent):
        super().__init__(parent)
        field = self._addField('New script name:', StringField(128))
        field.textChanged.connect(lambda name: self.setInputValid(self.isNameLegal(name)))
        self._getValue = field.getValue

    def _setValue(self, newValue):
        field = self.layout().itemAt(0, QFormLayout.FieldRole).widget()
        field.setValue(newValue)
        field.setFocus()
        field.textChanged.emit(newValue)
