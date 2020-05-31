from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


class ConfirmCloseMessage(QMessageBox):
    def __init__(self, editor):
        super().__init__(QMessageBox.Question, 'Unsaved changes in open script',
            f'The script "{editor.scriptName}" has unsaved changes.\n'
            'If you close it now, these changes will be lost.\n'
            'What do you want to do?'
        )
        self._editor = editor
        self._discard = self.addButton('Discard changes', QMessageBox.DestructiveRole)
        self.addButton('Keep editing', QMessageBox.RejectRole)

    def exec(self):
        if self._editor.scriptName and self._editor.isModified():
            super().exec()
            if self.clickedButton() != self._discard:
                self._editor.setFocus(Qt.OtherFocusReason)
                return False
        return True
