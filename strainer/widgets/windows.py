from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QSplitter, QDialog, QFormLayout, QDialogButtonBox
from qtawesome import icon

from ..controls import *
from .editor import Editor
from .reference import Reference
from .tree import Tree


class MainWindow(QMainWindow):
    def __init__(self, all_actions):
        super().__init__()
        self._actions = all_actions

        splitter = QSplitter()
        self.setCentralWidget(QFrame(self))
        QHBoxLayout(self.centralWidget()).addWidget(splitter)

        self.setWindowTitle('Strainer')
        self.setWindowIcon(icon('mdi.filter'))
        self.menuBar().addMenu(AccountMenu(self))
        self.menuBar().addMenu(ScriptMenu(self))
        self.menuBar().addMenu(EditMenu(self))

        self._tree = Tree(splitter)
        self._editor = Editor(splitter)
        self._reference = Reference(splitter)

    def action(self, action_type):
        return self._actions[action_type]

    def tree(self):
        return self._tree

    def editor(self):
        return self._editor

    def reference(self):
        return self._reference

class AccountWindow(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        layout = QFormLayout()
        layout.addRow('Display name:', StringField())
        layout.addRow('Server address:', StringField())
        layout.addRow('Server port:', IntegerField())
        layout.addRow('User name:', StringField())
        layout.addRow('Password:', PasswordField())
        layout.addRow('Use STARTTLS:', CheckboxField('enable'))
        layout.addRow('Authentication:', OptionsField([
            ('Automatic', None),
            ('Digest MD5', 'DIGEST-MD5'),
            ('Plain', 'PLAIN'),
            ('Login', 'LOGIN'),
        ]))
        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Discard)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        # Hacky hack because DestructiveRole for some reason doesn't close the window
        buttons.addButton(buttons.buttons()[-1], QDialogButtonBox.RejectRole)
        layout.addRow(buttons)
        self.setLayout(layout)

    def exec(self, values = None):
        if values:
            self.setWindowTitle('Change account settings')
            self.setWindowIcon(icon('mdi.account-edit'))
        else:
            self.setWindowTitle('Add new account')
            self.setWindowIcon(icon('mdi.account-plus'))
            values = ('New account', '', 4190, '', '', False, None)
        layout = self.layout()
        for i, value in enumerate(values):
            layout.itemAt(i, QFormLayout.FieldRole).widget().setValue(value)
        layout.itemAt(0, QFormLayout.FieldRole).widget().setFocus()
        if super().exec() == QDialog.Accepted:
            return [layout.itemAt(i, QFormLayout.FieldRole).widget().getValue() for i in range(layout.rowCount() - 1)]
        else:
            return None
