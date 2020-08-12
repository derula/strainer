from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWidgets import QApplication

from ..actions import HomePage, PreviousPage, NextPage, ReloadPage, CopyUrl, FindInPage
from ..controls import NavigateMenu
from ..types import FindDirection, FindOptions, FindQuery
from .base import Menu, MenuMixin, Find, FindMixin


class Reference(MenuMixin, FindMixin, QWebEngineView):
    _menu = Menu(
        NavigateMenu,
        {
            HomePage: 'home', PreviousPage: 'back', NextPage: 'forward',
            ReloadPage: 'stopOrReload', CopyUrl: 'copyUrl',
        },
        ('urlChanged',)
    )
    _find = Find(FindInPage, FindOptions(True))
    __make_url = 'https://thsmi.github.io/sieve-reference/en/{}.html'.format

    def __init__(self, parent):
        super().__init__(parent)
        self._isLoading = False

        def setLoading(value):
            self._isLoading = value
            self.updateMenu()
        self.loadStarted.connect(self.onLoadStarted)
        self.loadFinished.connect(self.onLoadFinished)
        self.home()

    def onLoadStarted(self):
        self._isLoading = True
        self.window().statusBar().showMessage(f'Communicating with {self.url().host()}, please wait...')
        self.updateMenu()

    def onLoadFinished(self):
        self._isLoading = False
        self.window().statusBar().clearMessage()
        self.updateMenu()

    def isHome(self):
        return self.url().matches(self._make_url(), QUrl.StripTrailingSlash | QUrl.NormalizePathSegments)

    def isLoading(self):
        return self._isLoading

    def home(self):
        self.setUrl(self._make_url())

    def browse(self, category, page):
        self.setUrl(self._make_url(category, 'core', page))

    def stopOrReload(self):
        (self.stop if self._isLoading else self.reload)()

    def copyUrl(self):
        QApplication.clipboard().setText(self.url().toString())
        # The WebAction doesn't say it's disabled if no link is active,
        # but it just doesn't copy anything in this case.
        # So we first copy the page URL, then overwrite it with the
        # currently selected link's URL (if any).
        self.page().triggerAction(QWebEnginePage.CopyLinkToClipboard)
        # (If the user first right-clicks a link, then clicks the
        # "copy link" somewhere else, it will still copy that.
        # I didn't find much we could do about it.)

    def sizeHint(self):
        return QSize(300, 600)

    def _make_url(self, *components):
        if not components:
            components = ('index',)
        return QUrl(self.__make_url('/'.join(components)))

    def _findNext(self, query: FindQuery):
        flags = 0
        if query.direction == FindDirection.Backward:
            flags |= QWebEnginePage.FindBackward
        if query.options.caseSensitive:
            flags |= QWebEnginePage.FindCaseSensitively
        self.findText(query.expression, QWebEnginePage.FindFlags(flags), query.callback)

    def _cancelFind(self):
        self.findText('')
