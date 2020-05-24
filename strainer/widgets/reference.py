from PyQt5.QtCore import QSize, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView


class Reference(QWebEngineView):
    __make_url = 'https://thsmi.github.io/sieve-reference/en/{}.html'.format

    def __init__(self):
        super().__init__()
        self.home()

    def home(self):
        self.setUrl(self._make_url())

    def browse(self, category, page):
        self.setUrl(self._make_url(category, 'core', page))

    def sizeHint(self):
        return QSize(300, 600)

    def _make_url(self, *components):
        if not components:
            components = ('index',)
        return QUrl(self.__make_url('/'.join(components)))
