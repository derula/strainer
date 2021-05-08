from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Sequence


class ValueTokens(Dict[bytes, Sequence[str]]):
    def __init__(self, *args, _: Sequence[str] = (), **kwargs):
        self._fallback = _
        super().__init__(*args, **kwargs)

    def __getitem__(self, key: Any):
        try:
            return super().__getitem__(key)
        except KeyError:
            return self._fallback


@dataclass
class Tag:
    name: str
    one_of: Sequence[bytes] = ()
    value_tokens: ValueTokens = field(default_factory=ValueTokens)
    required: bool = False


class Tags:
    def __init__(self, *specs: Tag):
        self._specs = specs
        self._tags = {tag: spec for spec in specs for tag in spec.one_of}

    def __iter__(self):
        yield from self._specs

    def __getitem__(self, key: bytes):
        return self._tags[key]

    def __contains__(self, key: bytes):
        return key in self._tags


over_under = Tag('`:over` or `:under`', (b':over', b':under',), ValueTokens(_=('number',)), True)
comparator = Tag('comparator', (b':comparator',), ValueTokens(_=('string',)))
match_type = Tag('match type', (b':is', b':contains', b':matches',))
address_part = Tag('address part', (b':localpart', b':domain', b':all'))
body_transform = Tag('body transform', (b':raw', b':content', b':text'), ValueTokens({b':content': ('string_list',)}))
