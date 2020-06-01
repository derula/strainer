from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QTreeWidgetItem

from .base import *


class AddAccount(MyAction):
    _text = '&Add account'
    _info = 'Configura a new ManageSieve account.'
    _icon = 'mdi.account-plus'
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Insert)

    def _shouldEnable(self, item):
        return item is not None

class EditAccount(NonEmptyAction):
    _text = 'Account &settings'
    _info = 'Change settings of this ManageSieve account.'
    _icon = 'mdi.account-edit'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Return)

class RemoveAccount(NonEmptyAction):
    _text = '&Remove account'
    _info = "Remove this ManageSieve account's settings from Strainer."
    _icon = 'mdi.account-remove'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.SHIFT | Qt.Key_Delete)

class ReloadAccount(NonEmptyAction):
    _text = 'Re&load account'
    _info = 'Reload the scripts list for this ManageSieve account.'
    _icon = 'mdi.account-convert'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.Key_F5)

class NewScript(NonEmptyAction):
    _text = '&New script'
    _info = 'Create a new script and add it to this ManageSieve account.'
    _icon = 'mdi.file-plus'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.Key_Insert)

class RenameScript(ScriptAction):
    _text = '&Rename script'
    _info = "Change the name under which this script is stored in this ManageSieve account."
    _icon = 'mdi.file-edit'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.Key_F2)

class DeleteScript(ScriptAction):
    _text = '&Delete script'
    _info = 'Permanently delete this script from this ManageSieve account.'
    _icon = 'mdi.file-remove'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.Key_Delete)

class OpenScript(ScriptAction):
    _text = '&Open script'
    _info = 'Open this script for editing. Any other open script will be closed.'
    _icon = 'mdi.file-download'
    _signal = pyqtSignal(QTreeWidgetItem)
    _shortcut = QKeySequence(Qt.Key_Return)

    def _shouldEnable(self, item):
        return super()._shouldEnable(item) and not item.open

class ActivateScript(MyStatefulAction):
    _texts = ('&Activate script', 'De&activate script')
    _infos = (
        'Activate this script to be used for new incoming email from now on.',
        'Deactivate this script, disabling Sieve filtering for this Account.'
    )
    _icons = ('mdi.file-check', 'mdi.file')
    _signal = pyqtSignal(QTreeWidgetItem)

    def _getState(self, item):
        return item and item.parent() and item.active
