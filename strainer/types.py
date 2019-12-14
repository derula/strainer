from enum import Enum, auto
from typing import NamedTuple, Optional


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
    def unserialize(cls, values):
        values['port'] = _get_int(values, 'port', 4190)
        values['starttls'] = bool(_get_int(values, 'starttls', 0))
        values.setdefault('authmech', None)
        return cls(**values)

    def serialize(self):
        result = self._asdict()
        del result['name']
        if self.authmech is None:
            del result['authmech']
        result['starttls'] = int(self.starttls)
        return result

class TreeItemStatus(Enum):
    Normal = auto()
    Loading = auto()
    Error = auto()
