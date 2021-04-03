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
                self.add_error(command_name, 'Command {} is not allowed here.', command_name)
            last_command = command_name.value
            if last_command == b'require' and arguments.positional_arguments:
                self.require(arguments.positional_arguments[0].children)

    def command(self, command_type: str, domain: dict, command_name: Token, arguments: Tree,
                block: Optional[Tree] = None):
        command_spec, found_block = domain.get(command_name.value), self.block(block)
        if command_spec is None:
            self.add_error(command_name, 'Unknown {} `{}`. Are you missing a `require`?', command_type, command_name)
            return None, None
        arguments = Arguments(command_spec, command_name, arguments)
        self.extend(arguments)
        comparator = arguments.tagged_arguments.get(b':comparator')
        if comparator and comparator[0].value not in self._comparators:
            self.add_error(comparator[0], 'Comparator missing respective `require`.')
        for test in arguments.tests:
            self.command('test', self._tests, *test.children)
        if not command_spec.has_block and found_block:
            self.add_error(command_name, 'Command does not allow specifying a block.')
        elif command_spec.has_block and not found_block:
            self.add_error(command_name, 'Command requires a block.')
        return command_spec, arguments

    def require(self, caps: Sequence[Token]):
        for cap in caps:
            if cap.value.startswith(b'comparator-'):
                comp = cap.value[11:]
                if comp in self._comparators:
                    self.add_warning(cap, 'Comparator `{}` required twice.', comp)
                elif comp not in self._comparators:
                    self.add_warning(cap, 'Comparator `{}` not supported.', comp)
                self._comparators.add(comp)
                continue
            if cap.value not in spec.capabilities:
                self.add_warning(cap, 'Capability `{}` not supported.', cap)
                continue
            cap = spec.capabilities[cap.value]
            self._commands.update(cap.commands)
            self._tests.update(cap.tests)

    def block(self, block: Optional[Tree]):
        try:
            block = block.children[0].children
        except (AttributeError, IndexError):
            return False
        self.commands(block, spec.block_start)
        return True
