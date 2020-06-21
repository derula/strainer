from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLineEdit, QCheckBox, QComboBox
from PyQt5.QtGui import QIntValidator


class StringField(QLineEdit):
    def __init__(self, max_len=255):
        super().__init__()
        self.setMaxLength(max_len)

    def setValue(self, newValue):
        self.setText(newValue)

    def getValue(self):
        return self.text()


class PasswordField(StringField):
    def __init__(self):
        super().__init__()
        self.setEchoMode(QLineEdit.Password)


class IntegerField(QLineEdit):
    def __init__(self, min=0, max=65535):
        super().__init__()
        self.setValidator(QIntValidator(min, max))

    def setValue(self, newValue):
        self.setText(str(newValue))

    def getValue(self):
        return int(self.text())


class CheckboxField(QCheckBox):
    def __init__(self, text=''):
        super().__init__()
        self.setText(text)

    def setValue(self, newValue):
        self.setCheckState(Qt.Checked if newValue else Qt.Unchecked)

    def getValue(self):
        return bool(self.checkState())


class OptionsField(QComboBox):
    def __init__(self, options=[], editable=False):
        super().__init__()
        for args in options:
            self.addItem(*args)
        self.setEditable(editable)

    def setValue(self, newValue):
        self.setCurrentIndex(self.findData(newValue))

    def getValue(self):
        return self.currentData()
