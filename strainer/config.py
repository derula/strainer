import base64
import configparser
import os
import uuid
import struct

from cryptography import fernet

from .types import Account


def _get_config_root():
    if 'nt' in os.name:
        return os.environ.get('APPDATA')
    else:
        return os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.environ['HOME'], '.config')

def _get_config_dir():
    path = os.path.join(_get_config_root(), 'strainer')
    os.makedirs(path, exist_ok=True)
    return path

class Accounts:
    def __init__(self, filename):
        self._filename = filename
        self._parser = configparser.ConfigParser()
        self._parser.read(filename)
        self._key = self._get_key()

    @property
    def all(self):
        for section in self._parser.sections():
            yield Account.unserialize(dict(self._parser.items(section), name=section), self._key)

    def add(self, account):
        self._parser[account.name] = account.serialize(self._key)
        self._save()

    def update(self, old_name, account):
        self._parser.remove_section(old_name)
        self.add(account)

    def remove(self, account):
        self._parser.remove_section(account.name)
        self._save()

    def _save(self):
        with open(self._filename, 'w') as f:
            self._parser.write(f)

    def _get_key(self):
        path = os.path.join(config_dir, 'key.bin')
        try:
            with open(path, 'rb') as f:
                key = f.read()
        except FileNotFoundError:
            key = os.urandom(32)
            with open(path, 'wb') as f:
                f.write(key)
        key = bytearray(key)
        for i, b in enumerate((struct.pack('Q', uuid.getnode())[:-2] * 6)[:-4]):
            key[i] ^= b
        return fernet.Fernet(base64.urlsafe_b64encode(key))

config_dir = _get_config_dir()
accounts = Accounts(os.path.join(config_dir, 'accounts.ini'))
