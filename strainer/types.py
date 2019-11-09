from enum import Enum, auto
from typing import NamedTuple, Optional


class Account(NamedTuple):
    name: str
    server: str
    port: int
    login: str
    passwd: str
    starttls: str
    authmech: Optional[str]

class AccountStatus(Enum):
    Normal = auto()
    Loading = auto()
    Error = auto()

class ScriptStatus(Enum):
    Normal = auto()
    Active = auto()
