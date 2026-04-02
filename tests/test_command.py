# tests/test_commands.py
from command.Commands import Commands

def test_command_error():
    """Validate that the custom user define command error 
    message is loaded"""

    cmd = Commands(device_cmd_filename="XS1234_TEST.json")
    response = cmd.process_command("not a command")
    
    assert response is not None
    assert response == 'That command is not valid'

def test_process_level_zero_command():
    cmd = Commands(device_cmd_filename="XS1234_TEST.json")
    response = cmd.process_command("show version")
    
    assert response is not None
    assert response == 'Simulated Device v1.0\r\nOS: CustomOS'

def test_process_level_one_command():
    cmd = Commands(device_cmd_filename="XS1234_TEST.json")
    response = cmd.process_command("enabled")
    
    assert response is not None
    assert response == 'Admin enabled'

def test_process_level_two_command():
    cmd = Commands(device_cmd_filename="XS1234_TEST.json")

    # Level ONE
    response = cmd.process_command("enabled")

    assert response is not None
    assert response == 'Admin enabled'

    # Level TWO
    response = cmd.process_command("enable vlan")

    assert response is not None
    assert response == 'VLAN 1'

    # Execution
    response = cmd.process_command("set vlan X")

    assert response is not None
    assert response == 'Vlan X Enabled'

def test_traverse_levels():
    """Traverse JSON file to deep=2 and return to the root of the file"""

    cmd = Commands(device_cmd_filename="XS1234_TEST.json")

    # Level ONE
    response = cmd.process_command("enabled")
    assert response is not None
    assert response == 'Admin enabled'

    # Level TWO
    response = cmd.process_command("enable vlan")
    assert response is not None
    assert response == 'VLAN 1'

    # EXEC: Level TWO
    response = cmd.process_command("set vlan X")
    assert response is not None
    assert response == 'Vlan X Enabled'

    # EXIT: To level ONE
    response = cmd.process_command("quit")
    assert response is not None
    assert response == ''

    # EXEC: Level ONE
    response = cmd.process_command("show ip")
    assert response is not None
    assert response == 'IP Address: 192.168.1.1\r\nSubnet Mask: 255.255.255.0'

    # EXIT: To level ZERO
    response = cmd.process_command("quit")
    assert response is not None
    assert response == ''
    
    # EXEC: Level ZERO
    response = cmd.process_command("show version")
    assert response is not None
    assert response == 'Simulated Device v1.0\r\nOS: CustomOS'