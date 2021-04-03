from __future__ import annotations
from typing import Optional, Sequence

from lark import Token, Tree

from .arguments import Arguments
from .issues import IssueCollector
from . import spec


class SemanticChecker(IssueCollector):
    def __init__(self):
        super().__init__()
        self._commands = spec.core_commands.copy()
        self._tests = spec.core_tests.copy()
        self._comparators = {b'i;ascii-casemap', b'i;octet'}

    def check(self, ast: Tree):
        self.issues.clear()
        self.commands(ast.children, spec.document_start)
        return self

    def commands(self, commands: Sequence[Tree], last_command):
        for command in commands:
            command_name, *_ = command.children
            command_spec, arguments = self.command('control / action', self._commands, *command.children)
            if command_spec and command_spec.must_follow is not None and last_command not in command_spec.must_follow:
                self.add_error(command_name, f'Command {command_name} is not allowed here.')
            last_command = command_name.value
            if last_command == b'require' and arguments.positional_arguments:
                self.require(arguments.positional_arguments[0].children)

    def command(self, command_type: str, domain: dict, command_name: Token, arguments: Tree,
                block: Optional[Tree] = None):
        try:
            command_spec = domain[command_name.value]
        except KeyError:
            self.add_error(command_name, f'Unknown {command_type} `{command_name}`. Are you missing a `require`?')
            return None, None  # TODO: still check block in this case!
        arguments = Arguments(command_spec, command_name, arguments, block)
        self.extend(arguments)
        comparator = arguments.tagged_arguments.get(b':comparator')
        if comparator and comparator[0].value not in self._comparators:
            self.add_error(comparator[0], 'Comparator missing respective `require`.')
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
                self.add_error(cap, f'Capability `{cap}` not supported.')
                continue
            cap = spec.capabilities[cap.value]
            self._commands.update(cap.commands)
            self._tests.update(cap.tests)
