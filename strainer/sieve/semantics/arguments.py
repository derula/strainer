from typing import ClassVar, Optional, Sequence

from lark import Token, Tree

from .issues import IssueCollector
from .spec import CommandSpec, TaggedArgumentSpec


class Arguments(IssueCollector):
    TAGS: ClassVar = {
        'over_under': TaggedArgumentSpec((b':over', b':under',), ('number',), True),
        'comparator': TaggedArgumentSpec((b':comparator',), ('string',)),
        'match_type': TaggedArgumentSpec((b':is', b':contains', b':matches',)),
        'address_part': TaggedArgumentSpec((b':localpart', b':domain', b':all')),
    }

    def __init__(self, command: CommandSpec, parent_token: Token, arguments: Tree):
        super().__init__()
        self.command = command
        self._parent = parent_token
        self.tagged_arguments = {}
        self._arg_stack = []
        self._current_tag = None
        self._parse_arguments(arguments.children[:-1])
        self._parse_tests(arguments.children[-1])

    def _parse_arguments(self, arguments: list):
        runaway_positionals = []
        for argument in arguments:
            argument_type = argument.type.lower() if isinstance(argument, Token) else 'string_list'
            if argument_type in self.TAGS or argument_type == 'tag':
                if self._current_tag:
                    self._consume_tag()
                if argument_type not in self.command.tagged_args:
                    self.add_error(argument, 'Argument {} not allowed for this command.', argument)
                if self._arg_stack:
                    self.add_error(argument, 'Tagged arguments must be placed at the start.')
                    runaway_positionals.extend(self._arg_stack)
                    self._arg_stack.clear()
                self._current_tag = (argument_type, argument)
            else:
                self._arg_stack.append((argument_type, argument))
        if self._current_tag:
            self._consume_tag()
        for tag_type in self.command.tagged_args:
            spec = self.TAGS[tag_type]
            if spec.required and not self.tagged_arguments.keys() & spec.one_of:
                self.add_error(self._parent, 'Argument {} must be specified.', tag_type)
        self._arg_stack = [*runaway_positionals, *self._arg_stack]
        self.positional_arguments = self._consume_args('positional arguments', self.command.positional_args,
                                                       self._parent, True)

    def _parse_tests(self, tests: Optional[Tree]):
        if self.command.test_type is None:
            if tests is not None:
                self.add_error(self._parent, 'Command does not allow specifying tests.')
        elif tests is None or tests.data != self.command.test_type:
            self.add_error(self._parent, 'Command requires a {}.', self.command.test_type)
        if self.command.test_type == 'test_list':
            self.tests = tests.children
        elif self.command.test_type == 'test':
            self.tests = [tests]
        else:
            self.tests = []

    def _consume_tag(self):
        tag_type, token = self._current_tag
        try:
            spec = self.TAGS[tag_type]
        except KeyError:
            spec = TaggedArgumentSpec()
        if token.value in self.tagged_arguments:
            self.add_error(token, 'Parameter `{}` was specified twice.', token)
        elif self.tagged_arguments.keys() & spec.one_of:
            self.add_error(token, 'Only one {} may be specified.', tag_type)
        token_value = token.value.decode('utf-8')  # Because Token is subclass of str, but gets confused
        self.tagged_arguments[token.value] = self._consume_args(f'values for tag {token_value}', spec.value_tokens,
                                                                token)
        self._current_tag = None

    def _consume_args(self, category: str, expected_types: Sequence[str], token: Token, exact: bool = False):
        actual_len = len(self._arg_stack)
        expected_len = len(expected_types)
        if actual_len < expected_len:
            self.add_error(token, 'Missing {} (got {}, expected {}).', category, actual_len, expected_len)
        elif exact and actual_len > expected_len:
            self.add_error(token, 'Too many {} (got {}, expected {}).', category, actual_len, expected_len)
        for i, (expected_type, (actual_type, value)) in enumerate(zip(expected_types, self._arg_stack)):
            if expected_type == 'string_list' and actual_type == 'string':
                # Commands accepting string lists always accept strings as well.
                # In the official grammar, this is expressed by allowing string_lists to be a string as well,
                # but this would break validation for commands that _only_ allow a string, not a list.
                # So instead, we replace strings with string lists here.
                self._arg_stack[i] = ('string_list', Tree('string_list', [value]))
                continue
            if expected_type != actual_type:
                self.add_error(token, 'Incorrect value type at position {} (got {}, expected {}).',
                               str(i+1), actual_type, actual_type)
        args = [arg[1] for arg in self._arg_stack[:expected_len]]
        self._arg_stack = self._arg_stack[expected_len:]
        return args
