from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Optional, Sequence

from . import tags
from .tags import Tags


@dataclass
class CommandSpec:
    positional_args: Sequence[str] = ()
    tags: Tags = field(default_factory=Tags)
    test_type: Optional[str] = None
    must_follow: Optional[Sequence[bytes]] = None
    has_block: bool = False


@dataclass
class Capability:
    commands: Mapping[bytes, CommandSpec] = field(default_factory=dict)
    tests: Mapping[bytes, CommandSpec] = field(default_factory=dict)
    comparators: Sequence[bytes] = ()


document_start = object()
block_start = object()
core_tags = Tags(tags.over_under, tags.comparator, tags.match_type, tags.address_part)
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
    b'size': CommandSpec(tags=Tags(tags.over_under)),
    b'header': CommandSpec(('string_list', 'string_list'), Tags(tags.comparator, tags.match_type)),
    b'address': CommandSpec(('string_list', 'string_list'), Tags(tags.comparator, tags.match_type, tags.address_part)),
}
capabilities = {
    b'fileinto': Capability(commands={b'fileinto': CommandSpec(('string',))}),
    b'envelope': Capability(tests={b'envelope': CommandSpec(('string_list', 'string_list'),
                                                            Tags(tags.comparator, tags.match_type,
                                                                 tags.address_part))}),
    b'body': Capability(tests={b'body': CommandSpec(('string_list',),
                                                    Tags(tags.comparator, tags.match_type, tags.body_transform))}),
    b'convert': Capability(commands={b'convert': CommandSpec(('string', 'string', 'string_list'))},
                           tests={b'convert': CommandSpec(('string', 'string', 'string_list'))}),
}
