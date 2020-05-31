from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox


class ConfirmCloseMessage(QMessageBox):
    _textTemplate = \
        'The script "{}" has unsaved changes.\n' \
        'If you close it now, these changes will be lost.\n' \
        'What do you want to do?'

    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Unsaved changes in open script')
        self.setIcon(QMessageBox.Question)
        self._discard = self.addButton('Discard changes', QMessageBox.DestructiveRole)
        self.addButton('Keep editing', QMessageBox.RejectRole)

    def exec(self):
        script = self.parent().openScript()
        if script and self.parent().editor().isModified():
            self.setText(self._textTemplate.format(script.name))
            self._discard.setFocus()
            super().exec()
            if self.clickedButton() != self._discard:
                self.parent().editor().setFocus(Qt.OtherFocusReason)
                return False
        return True
