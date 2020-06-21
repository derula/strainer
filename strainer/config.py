import base64
import os
import uuid
import struct

from cryptography import fernet
from PyQt5.QtCore import QSettings

from .types import Account


class AccountSettings(QSettings):
    def __init__(self, accountName=None):
        super().__init__()
        self._accountName = accountName

    def __enter__(self):
        self.beginGroup('accounts')
        if self._accountName:
            self.beginGroup(self._accountName)
        return self

    def __iter__(self):
        for section in self.childGroups():
            self.beginGroup(section)
            yield section
            self.endGroup()

    def __exit__(self, excType, excVal, excTb):
        self.endGroup()
        if self._accountName:
            self.endGroup()


class Accounts:
    def __init__(self):
        self._key = self._get_key()

    @property
    def all(self):
        with AccountSettings() as settings:
            for section in settings:
                values = {key: settings.value(key) for key in settings.childKeys()}
                yield Account.unserialize({**values, 'name': section}, self._key)

    def add(self, account):
        with AccountSettings(account.name) as settings:
            for entry in account.serialize(self._key).items():
                settings.setValue(*entry)

    def update(self, old_name, account):
        with AccountSettings() as settings:
            settings.remove(old_name)
        self.add(account)

    def remove(self, account):
        with AccountSettings() as settings:
            settings.remove(account.name)

    def _get_key(self):
        cfg_dir = os.path.normpath(os.path.dirname(QSettings().fileName()))
        path = os.path.join(cfg_dir, 'strainer.key')
        try:
            with open(path, 'rb') as f:
                key = f.read()
        except FileNotFoundError:
            key = os.urandom(32)
            os.makedirs(cfg_dir, exist_ok=True)
            with open(path, 'wb') as f:
                f.write(key)
        key = bytearray(key)
        for i, b in enumerate((struct.pack('Q', uuid.getnode())[:-2] * 6)[:-4]):
            key[i] ^= b
        return fernet.Fernet(base64.urlsafe_b64encode(key))
