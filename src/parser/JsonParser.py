import json
from pathlib import Path


class JsonParser:

    def __init__(self, filename: str):
        self.command_error: str = 'Invalid command!'
        self.command_exit: str = 'exit'
        self.raw_commands: dict = {}
        self.commands: list = []
        self.command_stack: list[str] = []

        # Resolve path relative to this file, not CWD
        # index 0=parser, 1=src, 2=root
        project_root = Path(__file__).resolve().parents[2]
        full_path = project_root / 'data' / filename

        with open(full_path, "r") as file:
            self.raw_commands = json.load(file)

        self.command_error = self.raw_commands.get('genericErrorMessage', self.command_error)
        self.command_exit = self.raw_commands.get('exitCommand', self.command_exit)
        self.commands = self.raw_commands.get('commands', [])

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_level_commands(self, commands: list[dict], stack: list[str]) -> list[dict]:
        """Recursively walk the command tree following the current stack,
        returning the command list at the current depth."""

        if not stack:
            return commands

        for cmd in commands:
            if cmd['input'] == stack[0]:
                return self._get_level_commands(
                    cmd.get('branchCommands', []),
                    stack[1:]
                )

        return []

    def _find_command(self, commands: list[dict], user_cmd: str) -> dict | None:
        """Find a command node by input string in a flat command list."""

        for cmd in commands:
            if cmd['input'] == user_cmd:
                return cmd
        return None

    def _push(self, value: str) -> None:
        self.command_stack.append(value)
        # print(f'Stack: {self.command_stack}')

    def _pop(self) -> None:
        self.command_stack.pop()
        # print(f'Stack: {self.command_stack}')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_command(self, user_cmd: str) -> str:
        """Process a user command and return the appropriate response."""

        # Handle exit
        if user_cmd == self.command_exit:
            if self.command_stack:
                self._pop()
                return ''
            return 'terminate'

        # Get the command list at the current stack depth (recursive traversal)
        current_level = self._get_level_commands(self.commands, self.command_stack)
        match = self._find_command(current_level, user_cmd)

        if match is None:
            return self.command_error

        # If this command opens a new branch, push it onto the stack
        if 'branchCommands' in match:
            self._push(user_cmd)

        return match.get('output', '')