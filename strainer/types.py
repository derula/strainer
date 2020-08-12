from dataclasses import dataclass
from enum import Enum, auto
from typing import Callable, NamedTuple, Optional

from PyQt5.QtCore import QByteArray


def _get_int(coll, key, default):
    try:
        return int(coll[key])
    except (KeyError, ValueError, TypeError):
        return default


class Account(NamedTuple):
    name: str
    server: str
    port: int
    login: str
    passwd: str
    starttls: bool
    authmech: Optional[str]

    @classmethod
    def unserialize(cls, values, pw_key=None):
        values['port'] = _get_int(values, 'port', 4190)
        values['starttls'] = bool(_get_int(values, 'starttls', 0))
        values.setdefault('authmech', None)
        if pw_key is not None:
            try:
                values['passwd'] = pw_key.decrypt(bytes(values['passwd'])).decode('utf-8')
            except Exception:
                values['passwd'] = ''
        return cls(**values)

    def serialize(self, pw_key=None):
        result = self._asdict()
        del result['name']
        if self.authmech is None:
            del result['authmech']
        result['starttls'] = int(self.starttls)
        if pw_key is not None:
            result['passwd'] = QByteArray(pw_key.encrypt(self.passwd.encode('utf-8')))
        return result


class TreeItemStatus(Enum):
    Normal = auto()
    Loading = auto()
    Error = auto()


class FindDirection(Enum):
    Forward = auto()
    Backward = auto()


class FindOptions(NamedTuple):
    caseSensitive: bool = False
    wholeWords: bool = False
    regularExpression: bool = False
    inSelection: bool = False


@dataclass(frozen=True)
class FindQuery:
    expression: str
    options: FindOptions = FindOptions()
    direction: FindDirection = FindDirection.Forward
    callback: Optional[Callable[[bool], None]] = None
