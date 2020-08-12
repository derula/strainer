from PyQt5.QtCore import Qt
from PyQt5.QtGui import QKeySequence

from .base import MyAction, MyStatefulAction


class HomePage(MyAction):
    _text = '&Home'
    _info = 'Return to the Sieve Language Reference start page.'
    _icon = 'mdi.home'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_Home)

    def _shouldEnable(self, reference):
        return not reference.isHome()


class PreviousPage(MyAction):
    _text = '&Back'
    _info = 'Go back to the last page in the browsing history.'
    _icon = 'mdi.arrow-left-bold-circle'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_Left)

    def _shouldEnable(self, reference):
        return reference.history().canGoBack()


class NextPage(MyAction):
    _text = '&Forward'
    _info = 'Go forward to the next page in the browsing history.'
    _icon = 'mdi.arrow-right-bold-circle'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_Right)

    def _shouldEnable(self, reference):
        return reference.history().canGoForward()


class ReloadPage(MyStatefulAction):
    _texts = ('&Reload', '&Stop')
    _infos = (
        'Reload the page currently opened in the browser.',
        'Cancel loading the page currently being accessed.',
    )
    _icons = ('mdi.refresh', 'mdi.stop-circle')
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_F5)

    def _getState(self, reference):
        return bool(reference.isLoading())


class CopyUrl(MyAction):
    _text = '&Copy URL'
    _info = 'Copy this URL (open or right-clicked) to the clipboard.'
    _icon = 'mdi.content-copy'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_C)

    def _shouldEnable(self, reference):
        return True


class FindInPage(MyAction):
    _text = '&Find'
    _info = 'Open the find panel to search for text in this page.'
    _icon = 'mdi.file-document-box-search'
    _shortcut = QKeySequence(Qt.ALT | Qt.Key_F)

    def _shouldEnable(self, reference):
        return not reference.isLoading()
