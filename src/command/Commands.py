
from parser.JsonParser import JsonParser

class Commands():
    def __init__(self, device_cmd_filename: str):
        self.json_parser = JsonParser(filename=device_cmd_filename)

    def process_command(self, command: str):
        """Processes CLI commands and returns appropriate responses."""
        # commands = {
        #     "show version": "Simulated Device v1.0\r\nOS: CustomOS",
        #     "show ip": "IP Address: 192.168.1.1\r\nSubnet Mask: 255.255.255.0",
        # }

        return self.json_parser.get_command(user_cmd=command)