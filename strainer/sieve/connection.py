from PyQt5.QtCore import QThread
from sievelib import managesieve


class SieveConnection(QThread):
    def __init__(self, account, success = None, failure = None, always = None):
        super().__init__()
        self._account = account
        if success is not None: self._success = success
        if failure is not None: self._failure = failure
        if always is not None: self._always = always
        self.start()

    def run(self):
        _, server, port, login, passwd, starttls, authmech = self._account
        try:
            conn = managesieve.Client(server, port)
            if not conn.connect(login, passwd, starttls=starttls, authmech=authmech):
                raise managesieve.Error('Failed to authenticate to server')
        except Exception as e:
            e = self._failure(e)
            if e is not None:
                raise e
        else:
            self._success(conn)
        finally:
            self._always()

    def _success(self, conn):
        pass

    def _failure(self, e):
        pass

    def _always(self):
        pass
