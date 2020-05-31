from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox

from .base import DialogTitle, ConfirmMessage


class ConfirmCloseMessage(ConfirmMessage):
    _title = DialogTitle('mdi.file-star', 'Unsaved changes in open script')
    _textTemplate = \
        'The script "{}" has unsaved changes.\n' \
        'If you close it now, these changes will be lost.\n' \
        'What do you want to do?'
    _acceptText = 'Discard changes'
    _rejectText = 'Keep editing'

    def exec(self):
        script = self.parent().openScript()
        if script and self.parent().editor().isModified():
            return super().exec(script.name)
        return True

class ConfirmRemoveAccount(ConfirmMessage):
    _title = DialogTitle('mdi.account-remove', 'Remove current account')
    _textTemplate = \
        'You are about to remove the account "{}" from Strainer.\n' \
        'Filters will remain on the server and in effect (if active).\n' \
        'What do you want to do?'
    _acceptText = 'Remove account'
    _rejectText = 'Keep account'

class ConfirmDeleteScript(ConfirmMessage):
    _title = DialogTitle('mdi.file-remove', 'Remove selected script')
    _textTemplate = \
        'You are about to delete the script "{}" from the account "{}".\n' \
        'This action cannot be undone, and the script contents will be lost.\n' \
        'What do you want to do?'
    _acceptText = 'Delete script'
    _rejectText = 'Keep script'
