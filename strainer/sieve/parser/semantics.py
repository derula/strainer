from __future__ import annotations
from dataclasses import dataclass, field
from re import compile
from typing import ClassVar, Mapping, Optional, Sequence

from lark import Transformer, v_args, Token, Tree


@dataclass
class SieveScript:
    ast: Tree

    def check(self):
        SemanticChecker().check(self.ast)

    def __getattr__(self, attr):
        return getattr(self.ast, attr)


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
    comparators: Sequence[bytes] = ()


@dataclass
class TaggedArgumentSpec:
    one_of: Sequence[bytes] = ()
    value_tokens: Sequence[str] = ()
    required: bool = False


class SemanticTransformer(Transformer):
    ESCAPED_CHARACTER = compile(br'\\(.)')
    start = v_args(inline=True)(SieveScript)

    @v_args(inline=True)
    def command_name(self, token: Token):
        return token

    tag = test_name = command_name

    @v_args(inline=True)
    def string(self, token: Token):
        token.value = self.ESCAPED_CHARACTER.sub(br'\1', token.value[1:-1])
        return token

    @v_args(inline=True)
    def text(self, token: Token):
        text = token.value
        token.value = text.replace(b'\r\n..', b'\r\n.')[text.index(b'\r\n')+2:-3]
        return token


class SemanticError(Exception):
    def __init__(self, token: Token, message: str):
        self.line = token.line
        self.column = token.column
        super().__init__(f'Semantic error in line {token.line}, column {token.column}: {message}')


class ParentSemanticError(Exception):
    def __init__(self, message: str):
        self.message = message

    def emit(self, parent: Token):
        return SemanticError(parent, self.message)


class SemanticChecker:
    DOCUMENT_START = object()
    BLOCK_START = object()
    CORE_COMMANDS = {
        b'keep': CommandSpec(),
        b'stop': CommandSpec(),
        b'discard': CommandSpec(),
        b'redirect': CommandSpec(('string',)),
        b'require': CommandSpec(('string_list',), must_follow=(DOCUMENT_START, b'require')),
        b'if': CommandSpec(test_type='test', has_block=True),
        b'elsif': CommandSpec(test_type='test', has_block=True, must_follow=(b'if', b'elsif')),
        b'else': CommandSpec(has_block=True, must_follow=(b'if', b'elsif')),
    }
    CORE_TESTS = {
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
    CAPABILITIES = {
        b'fileinto': Capability(commands={b'fileinto': CommandSpec(('string',))}),
        b'envelope': Capability(tests={b'envelope': CommandSpec(('string_list', 'string_list'),
                                                                ('comparator', 'match_type', 'address_part'))}),
    }

    def __init__(self):
        self._commands = self.CORE_COMMANDS.copy()
        self._tests = self.CORE_TESTS.copy()
        self._comparators = {b'i;ascii-casemap', b'i;octet'}

    def check(self, ast: Tree):
        self.commands(ast.children, self.DOCUMENT_START)

    def commands(self, commands: Sequence[Tree], last_command):
        for command in commands:
            command_name, *_ = command.children
            spec, arguments = self.command('control / action', self._commands, *command.children)
            if spec.must_follow is not None and last_command not in spec.must_follow:
                raise SemanticError(command_name, f'Command {command_name} is not allowed here.')
            last_command = command_name.value
            if last_command == b'require':
                self.require(arguments.positional_arguments[0].children)

    def command(self, command_type: str, domain: dict, command_name: Token, arguments: Tree,
                block: Optional[Tree] = None):
        try:
            command_spec = domain[command_name.value]
        except KeyError:
            raise SemanticError(command_name, f'Unknown {command_type} `{command_name}`. Are you missing a `require`?')
        try:
            arguments = Arguments(command_spec, arguments, block)
        except ParentSemanticError as e:
            raise e.emit(command_name)
        comparator = arguments.tagged_arguments.get(b':comparator')
        if comparator is not None and comparator[0].value not in self._comparators:
            raise SemanticError(comparator[0], f'Comparator missing respective `require`.')
        for test in arguments.tests:
            self.command('test', self._tests, *test.children)
        if arguments.block is not None:
            self.commands(arguments.block, self.BLOCK_START)
        return command_spec, arguments

    def require(self, caps: Sequence[Token]):
        for cap in caps:
            if cap.value.startswith(b'comparator-'):
                self._comparators.add(cap.value[11:])
                continue
            if cap.value not in self.CAPABILITIES:
                raise SemanticError(cap, f'Capability `{cap}` not supported.')
            cap = self.CAPABILITIES[cap.value]
            self._commands.update(cap.commands)
            self._tests.update(cap.tests)


class Arguments:
    TAGS: ClassVar = {
        'over_under': TaggedArgumentSpec((b':over', b':under',), ('number',), True),
        'comparator': TaggedArgumentSpec((b':comparator',), ('string',)),
        'match_type': TaggedArgumentSpec((b':is', b':contains', b':matches',)),
        'address_part': TaggedArgumentSpec((b':localpart', b':domain', b':all')),
    }

    def __init__(self, command: CommandSpec, arguments: Tree, block: Optional[Tree] = None):
        self.command = command
        self.tagged_arguments = {}
        self._arg_stack = []
        self._current_tag = None
        self._parse_arguments(arguments.children[:-1])
        self._parse_special_arguments(arguments.children[-1], block)

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
                raise ParentSemanticError(f'One of {spec.one_of} must be specified.')
        self._consume_args('positional arguments', self.command.positional_args)

    def _parse_special_arguments(self, tests: Optional[Tree], block: Optional[Tree]):
        if self.command.test_type is None:
            if tests is not None:
                raise ParentSemanticError('Command does not allow specifying tests.')
        elif tests is None or tests.data != self.command.test_type:
            raise ParentSemanticError(f'Command requires a {self.command.test_type}.')
        if self.command.test_type == 'test_list':
            self.tests = tests.children
        elif self.command.test_type == 'test':
            self.tests = [tests]
        else:
            self.tests = []
        try:
            self.block = block.children[0].children
        except (AttributeError, IndexError):
            self.block = None
        if not self.command.has_block:
            if self.block is not None:
                raise ParentSemanticError('Command does not allow specifying a block.')
        elif self.block is None:
            raise ParentSemanticError('Command requires a block.')

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
        try:
            self._consume_args(f'values for tag {token.value}', spec.value_tokens, token.value)
        except ParentSemanticError as e:
            raise e.emit(token)
        self._current_tag = None

    def _consume_args(self, category: str, expected_types: Sequence[str], key: Optional[bytes] = None):
        actual_len = len(self._arg_stack)
        expected_len = len(expected_types)
        if actual_len < expected_len:
            raise ParentSemanticError(f'Missing {category} (got {actual_len}, expected {expected_len}).')
        if key is None and actual_len > expected_len:
            raise ParentSemanticError(f'Too many {category} (got {actual_len}, expected {expected_len}).')
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
                raise ParentSemanticError(f'Incorrect value type at position {i+1} '
                                          f'(got {actual_type}, expected {expected_type}).')
        args = [arg[1] for arg in self._arg_stack[:expected_len]]
        self._arg_stack = self._arg_stack[expected_len:]
        if key is not None:
            self.tagged_arguments[key] = args
        else:
            self.positional_arguments = args
