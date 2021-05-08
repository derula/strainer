from typing import Optional, Sequence

from lark import Token, Tree

from .issues import IssueCollector
from .spec import CommandSpec
from .tags import Tag


class Arguments(IssueCollector):
    UNKNOWN_TAG = Tag('unknown tag')

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
            if argument_type in ('known_tag', 'tag'):
                if self._current_tag:
                    self._consume_tag()
                if argument.value.lower() not in self.command.tags:
                    self.add_error(argument, 'Command `{}` takes no `{}` argument.', self._parent, argument)
                if self._arg_stack:
                    self.add_error(argument, 'Tagged arguments must be placed at the beginning.')
                    runaway_positionals.extend(self._arg_stack)
                    self._arg_stack.clear()
                self._current_tag = (argument_type, argument)
            else:
                self._arg_stack.append((argument_type, argument))
        if self._current_tag:
            self._consume_tag()
        for spec in self.command.tags:
            if spec.required and not self.tagged_arguments.keys() & spec.one_of:
                self.add_command_error('requires {}', spec.name)
        self._arg_stack = [*runaway_positionals, *self._arg_stack]
        self.positional_arguments = self._consume_args('positional arguments', self.command.positional_args,
                                                       self._parent, True)

    def _parse_tests(self, tests: Optional[Tree]):
        self.tests = []
        if tests is None:
            if self.command.test_type is None:
                return
        else:
            if tests.data == 'test_list':
                self.tests = tests.children
            elif tests.data == 'test':
                self.tests = [tests]
            if tests.data == self.command.test_type:
                return
        if self.command.test_type is None:
            self.add_command_error('does not allow specifying tests')
        else:
            self.add_command_error('requires a {}', self.command.test_type)

    def _consume_tag(self):
        tag_type, token = self._current_tag
        try:
            spec = self.command.tags[token.value]
        except KeyError:
            spec = self.UNKNOWN_TAG
        if token.value in self.tagged_arguments:
            self.add_error(token, 'Argument `{}` was specified twice.', token)
        elif self.tagged_arguments.keys() & spec.one_of:
            self.add_error(token, 'Only one {} may be specified.', spec.name)
        token_value = token.value.decode('utf-8')  # Because Token is subclass of str, but gets confused
        self.tagged_arguments[token.value] = self._consume_args(f'values for tag {token_value}',
                                                                spec.value_tokens[token.value], token)
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

    def add_command_error(self, message: str, *args):
        self.add_error(self._parent, f'Command `{{}}` {message}.', self._parent, *args)
