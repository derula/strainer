from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from .base import *


class HomePage(MyAction):
    _text = '&Home'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_Home)
    _icon = 'mdi.home'

    def _shouldEnable(self, reference):
        return not reference.isHome()

class PreviousPage(MyAction):
    _text = '&Back'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_Left)
    _icon = 'mdi.arrow-left-bold-circle'

    def _shouldEnable(self, reference):
        return reference.history().canGoBack()

class NextPage(MyAction):
    _text = '&Forward'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_Right)
    _icon = 'mdi.arrow-right-bold-circle'

    def _shouldEnable(self, reference):
        return reference.history().canGoForward()

class ReloadPage(MyStatefulAction):
    _texts = ('&Reload', '&Stop')
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_F5)
    _icons = ('mdi.refresh', 'mdi.stop-circle')

    def _getState(self, reference):
        return bool(reference.isLoading())

class CopyUrl(MyAction):
    _text = '&Copy URL'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_C)
    _icon = 'mdi.content-copy'

    def _shouldEnable(self, reference):
        return True
