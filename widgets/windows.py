from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QSplitter, QDialog, QFormLayout, QDialogButtonBox

from .editor import Editor
from .fields import *
from .menus import ManageMenu
from .tree import Tree


class MainWindow(QMainWindow):
    def __init__(self, all_actions):
        super().__init__()
        self.setWindowTitle('Strainer')

        manage_menu = ManageMenu(self, all_actions)
        self.menuBar().addMenu(manage_menu)

        frame = QFrame(self)
        layout = QHBoxLayout()
        splitter = QSplitter()
        tree = Tree(manage_menu)
        splitter.addWidget(tree)
        splitter.addWidget(Editor())
        layout.addWidget(splitter)
        frame.setLayout(layout)
        self.setCentralWidget(frame)
        self._tree = tree

    @property
    def tree(self):
        return self._tree


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
        else:
            self.setWindowTitle('Add new account')
            values = ('New account', '', 4190, '', '', False, None)
        layout = self.layout()
        for i, value in enumerate(values):
            layout.itemAt(i, QFormLayout.FieldRole).widget().setValue(value)
        layout.itemAt(0, QFormLayout.FieldRole).widget().setFocus()
        if super().exec() == QDialog.Accepted:
            return [layout.itemAt(i, QFormLayout.FieldRole).widget().getValue() for i in range(layout.rowCount() - 1)]
        else:
            return None
