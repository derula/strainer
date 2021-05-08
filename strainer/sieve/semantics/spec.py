from __future__ import annotations
from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence, Union


@dataclass
class CommandSpec:
    positional_args: Sequence[str] = ()
    tagged_args: Sequence[str] = ()
    test_type: Optional[str] = None
    must_follow: Optional[Sequence[bytes]] = None
    has_block: bool = False


@dataclass
class Capability:
    commands: Mapping[bytes, CommandSpec] = field(default_factory=dict)
    tests: Mapping[bytes, CommandSpec] = field(default_factory=dict)
    tags: Mapping[str, TaggedArgumentSpec] = field(default_factory=dict)
    comparators: Sequence[bytes] = ()


@dataclass
class TaggedArgumentSpec:
    name: str
    one_of: Sequence[bytes] = ()
    value_tokens: Union[Sequence[str], Mapping[bytes, Sequence[str]]] = ()
    required: bool = False

    def __post_init__(self):
        if isinstance(self.value_tokens, (list, tuple)):
            self.value_tokens = dict.fromkeys(self.one_of, self.value_tokens)
        else:
            self.value_tokens = {**dict.fromkeys(self.one_of, ()), **self.value_tokens}


document_start = object()
block_start = object()
core_tags = {
    'over_under': TaggedArgumentSpec('`:over` or `:under`', (b':over', b':under',), ('number',), True),
    'comparator': TaggedArgumentSpec('comparator', (b':comparator',), ('string',)),
    'match_type': TaggedArgumentSpec('match type', (b':is', b':contains', b':matches',)),
    'address_part': TaggedArgumentSpec('address part', (b':localpart', b':domain', b':all')),
}
core_commands = {
    b'keep': CommandSpec(),
    b'stop': CommandSpec(),
    b'discard': CommandSpec(),
    b'redirect': CommandSpec(('string',)),
    b'require': CommandSpec(('string_list',), must_follow=(document_start, b'require')),
    b'if': CommandSpec(test_type='test', has_block=True),
    b'elsif': CommandSpec(test_type='test', has_block=True, must_follow=(b'if', b'elsif')),
    b'else': CommandSpec(has_block=True, must_follow=(b'if', b'elsif')),
}
core_tests = {
    b'true': CommandSpec(),
    b'false': CommandSpec(),
    b'not': CommandSpec(test_type='test'),
    b'allof': CommandSpec(test_type='test_list'),
    b'anyof': CommandSpec(test_type='test_list'),
    b'exists': CommandSpec(('string_list',)),
    b'size': CommandSpec(tagged_args=('over_under',)),
    b'header': CommandSpec(('string_list', 'string_list'), ('comparator', 'match_type')),
    b'address': CommandSpec(('string_list', 'string_list'), ('comparator', 'match_type', 'address_part')),
}
capabilities = {
    b'fileinto': Capability(commands={b'fileinto': CommandSpec(('string',))}),
    b'envelope': Capability(tests={b'envelope': CommandSpec(('string_list', 'string_list'),
                                                            ('comparator', 'match_type', 'address_part'))}),
    b'body': Capability(tests={b'body': CommandSpec(('string_list',), ('comparator', 'match_type', 'body_transform'))},
                        tags={'body_transform': TaggedArgumentSpec('body transform', (b':raw', b':content', b':text'),
                                                                   {b':content': ('string_list',)})})
}
