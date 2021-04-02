from __future__ import annotations
from typing import Optional, Sequence

from lark import Token, Tree

from .arguments import Arguments
from .errors import SemanticError, ParentSemanticError
from . import spec


class SemanticChecker:
    def __init__(self):
        self._commands = spec.core_commands.copy()
        self._tests = spec.core_tests.copy()
        self._comparators = {b'i;ascii-casemap', b'i;octet'}
        self._issues = []

    def check(self, ast: Tree):
        self._issues.clear()
        self.commands(ast.children, spec.document_start)
        if self._issues:
            raise self._issues[0]

    def commands(self, commands: Sequence[Tree], last_command):
        for command in commands:
            command_name, *_ = command.children
            try:
                command_spec, arguments = self.command('control / action', self._commands, *command.children)
            except SemanticError as e:
                self._issues.append(e)
                continue
            if command_spec.must_follow is not None and last_command not in command_spec.must_follow:
                self._issues.append(SemanticError(command_name, f'Command {command_name} is not allowed here.'))
            last_command = command_name.value
            if last_command == b'require':
                try:
                    self.require(arguments.positional_arguments[0].children)
                except SemanticError as e:
                    self._issues.append(e)

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
            raise SemanticError(comparator[0], 'Comparator missing respective `require`.')
        for test in arguments.tests:
            self.command('test', self._tests, *test.children)
        if arguments.block is not None:
            self.commands(arguments.block, spec.block_start)
        return command_spec, arguments

    def require(self, caps: Sequence[Token]):
        for cap in caps:
            if cap.value.startswith(b'comparator-'):
                self._comparators.add(cap.value[11:])
                continue
            if cap.value not in spec.capabilities:
                raise SemanticError(cap, f'Capability `{cap}` not supported.')
            cap = spec.capabilities[cap.value]
            self._commands.update(cap.commands)
            self._tests.update(cap.tests)
