from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFrame, QHBoxLayout, QSplitter, QDialog, QFormLayout, QDialogButtonBox, QMessageBox
from qtawesome import icon

from ..actions import SaveScript
from ..controls import *
from .editor import Editor
from .reference import Reference
from .tree import Tree


class ConfirmClose(QMessageBox):
    def __init__(self, scriptName):
        super().__init__(QMessageBox.Question, 'Unsaved changes in open script',
            f'The script "{scriptName}" has unsaved changes.\n'
            'If you close it now, these changes will be lost.\n'
            'What do you want to do?',
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
        )

class MainWindow(QMainWindow):
    def __init__(self, all_actions):
        super().__init__()
        self._actions = all_actions

        splitter = QSplitter()
        self.setCentralWidget(QFrame(self))
        QHBoxLayout(self.centralWidget()).addWidget(splitter)

        self.setWindowIcon(icon('mdi.filter'))
        self.menuBar().addMenu(AccountMenu(self))
        self.menuBar().addMenu(ScriptMenu(self))
        self.menuBar().addMenu(EditMenu(self))
        self.addToolBar(Toolbar(self))

        self._tree = Tree(splitter)
        self._editor = Editor(splitter)
        self._reference = Reference(splitter)
        self._editor.modificationChanged.connect(self.onModificationChanged)
        self.onModificationChanged()

    def action(self, action_type):
        return self._actions[action_type]

    def tree(self):
        return self._tree

    def editor(self):
        return self._editor

    def reference(self):
        return self._reference

    def onModificationChanged(self, isModified=False):
        title = 'Strainer'
        if self._editor.scriptName:
            title = f"{title} ({self._editor.scriptName}{'*' if isModified else ''})"
        self.setWindowTitle(title)

    def closeEvent(self, event):
        if self._editor.scriptName and self._editor.isModified():
            result = ConfirmClose(self._editor.scriptName).exec()
        else:
            result = QMessageBox.Discard
        if result == QMessageBox.Cancel:
            event.ignore()
            return
        if result == QMessageBox.Save:
            self._actions[SaveScript].trigger()
        event.accept()

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
