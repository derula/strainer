from typing import ClassVar, Optional, Sequence

from lark import Token, Tree

from .issues import SemanticError
from .spec import CommandSpec, TaggedArgumentSpec


class Arguments:
    TAGS: ClassVar = {
        'over_under': TaggedArgumentSpec((b':over', b':under',), ('number',), True),
        'comparator': TaggedArgumentSpec((b':comparator',), ('string',)),
        'match_type': TaggedArgumentSpec((b':is', b':contains', b':matches',)),
        'address_part': TaggedArgumentSpec((b':localpart', b':domain', b':all')),
    }

    def __init__(self, command: CommandSpec, parent_token: Token, arguments: Tree, block: Optional[Tree] = None):
        self.command = command
        self._parent = parent_token
        self.tagged_arguments = {}
        self._arg_stack = []
        self._current_tag = None
        self._parse_arguments(arguments.children[:-1])
        self._parse_tests(arguments.children[-1])
        self._parse_block(block)

    def _parse_arguments(self, arguments: list):
        for argument in arguments:
            argument_type = argument.type.lower() if isinstance(argument, Token) else 'string_list'
            if argument_type in self.TAGS or argument_type == 'tag':
                if self._current_tag:
                    self._consume_tag()
                if argument_type not in self.command.tagged_args:
                    raise SemanticError(argument, f'Argument `{argument.value}` not allowed for this command.')
                if self._arg_stack:
                    raise SemanticError(argument, 'Tagged arguments must be placed at the start.')
                self._current_tag = (argument_type, argument)
            else:
                self._arg_stack.append((argument_type, argument))
        if self._current_tag:
            self._consume_tag()
        for tag_type in self.command.tagged_args:
            spec = self.TAGS[tag_type]
            if spec.required and not self.tagged_arguments.keys() & spec.one_of:
                raise SemanticError(self._parent, f'One of {spec.one_of} must be specified.')
        self._consume_args('positional arguments', self.command.positional_args, self._parent)

    def _parse_tests(self, tests: Optional[Tree]):
        if self.command.test_type is None:
            if tests is not None:
                raise SemanticError(self._parent, 'Command does not allow specifying tests.')
        elif tests is None or tests.data != self.command.test_type:
            raise SemanticError(self._parent, f'Command requires a {self.command.test_type}.')
        if self.command.test_type == 'test_list':
            self.tests = tests.children
        elif self.command.test_type == 'test':
            self.tests = [tests]
        else:
            self.tests = []

    def _parse_block(self, block: Optional[Tree]):
        try:
            self.block = block.children[0].children
        except (AttributeError, IndexError):
            self.block = None
        if not self.command.has_block:
            if self.block is not None:
                raise SemanticError(self._parent, 'Command does not allow specifying a block.')
        elif self.block is None:
            raise SemanticError(self._parent, 'Command requires a block.')

    def _consume_tag(self):
        tag_type, token = self._current_tag
        try:
            spec = self.TAGS[tag_type]
        except KeyError:
            spec = TaggedArgumentSpec()
        if token.value in self.tagged_arguments:
            raise SemanticError(token, f'Parameter `{token.value}` was specified twice.')
        for other_name in spec.one_of:
            if other_name in self.tagged_arguments:
                raise SemanticError(token, f'Only one of `{token.value}` or `{other_name}` may be specified.')
        self._consume_args(f'values for tag {token.value}', spec.value_tokens, token, token.value)
        self._current_tag = None

    def _consume_args(self, category: str, expected_types: Sequence[str], token: Token, key: Optional[bytes] = None):
        actual_len = len(self._arg_stack)
        expected_len = len(expected_types)
        if actual_len < expected_len:
            raise SemanticError(token, f'Missing {category} (got {actual_len}, expected {expected_len}).')
        if key is None and actual_len > expected_len:
            raise SemanticError(token, f'Too many {category} (got {actual_len}, expected {expected_len}).')
        for i, expected_type in enumerate(expected_types):
            actual_type, value = self._arg_stack[i]
            if expected_type == 'string_list' and actual_type == 'string':
                # Commands accepting string lists always accept strings as well.
                # In the official grammar, this is expressed by allowing string_lists to be a string as well,
                # but this would break validation for commands that _only_ allow a string, not a list.
                # So instead, we replace strings with string lists here.
                self._arg_stack[i] = ('string_list', Tree('string_list', [value]))
                continue
            if expected_type != actual_type:
                raise SemanticError(token, f'Incorrect value type at position {i+1} '
                                           f'(got {actual_type}, expected {expected_type}).')
        args = [arg[1] for arg in self._arg_stack[:expected_len]]
        self._arg_stack = self._arg_stack[expected_len:]
        if key is not None:
            self.tagged_arguments[key] = args
        else:
            self.positional_arguments = args