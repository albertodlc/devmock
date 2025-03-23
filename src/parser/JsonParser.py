import json
from pathlib import Path

class JsonParser:
    raw_commands = {}

    command_error = 'Invalid command!'
    command_exit = 'exit'
    commands = []
    command_stack = []
    
    def __init__(self, filename: str):
        data = None

        # TODO: Improve this relative paths
        path = Path('data') / filename
        full_path = path.resolve()

        with open(full_path, "r") as file:
            self.raw_commands = json.load(file)     
        
        # TODO: init exit and invalid command
        if self.raw_commands['genericErrorMessage']:
            self.command_error = self.raw_commands['genericErrorMessage']
        
        if self.raw_commands['exitCommand']:
            self.command_exit = self.raw_commands['exitCommand']

        self.commands = self.raw_commands['commands']

    def _find_next_level_commands(self, levels_cmds: [], prev_search_cmd: str)  -> []:
        for level_cmd in levels_cmds:
            if level_cmd['input'] == prev_search_cmd:
                return level_cmd['branchCommands']

        return None

    def _find_next_level_command(self, levels_cmds: [], search_cmd: str)  -> {}:
        for level_cmd in levels_cmds:
            if level_cmd['input'] == search_cmd:
                return level_cmd

        return None

    def _add_to_stack(self, value: str):
        self.command_stack.append(value)

        print(f'Current CMD Stack status: {self.command_stack}')

    def _pop_from_stack(self):
        self.command_stack.pop()

        print(f'Current CMD Stack status: {self.command_stack}')

    def get_command(self, user_cmd: str):
        if user_cmd == self.command_exit and len(self.command_stack) > 0:
            self._pop_from_stack()

            return ''
        elif user_cmd == self.command_exit:
            return 'terminate'

        # Command in Level 1
        next_level_command = None

        if len(self.command_stack) == 0:
            for command in self.commands:
                if command['input'] == user_cmd:
                    if 'branchCommands' in command:
                        self._add_to_stack(user_cmd)

                    return command['output']
        # Command in a level > 1
        else:
            for stack_command in self.command_stack:
                next_level_commands = self._find_next_level_commands(self.commands, stack_command)

            next_level_command = self._find_next_level_command(next_level_commands, user_cmd)

        if next_level_command and next_level_command['input'] == user_cmd and 'branchCommands' in next_level_command:
            self._add_to_stack(user_cmd)
        
        # Si tiene siguiente nivel
        if next_level_command:
            return next_level_command['output']

        return self.command_error