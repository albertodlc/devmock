#!/usr/bin/env python
import logging
import socket
import sys
import threading
import paramiko
import traceback

from stream.ChannelBuffer import ChannelBuffer
from parser.JsonParser import JsonParser

logging.basicConfig()
logger = logging.getLogger()


if len(sys.argv) == 1:
    host_key = paramiko.RSAKey.generate(2048)
elif len(sys.argv) == 2:
    print("Private host RSA key filename received as argument.")
    host_key = paramiko.RSAKey(filename=key)
else:
    print("Private host RSA key needed as argument.")
    sys.exit(1)


class SSHServer(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username, password):
        """Authenticate user with a username and password."""
        if username == 'admin' and password == 'admin':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes):
        """Handles PTY requests for an interactive shell experience."""
        
        print(f"[+] PTY requested: {term}, Size: {width}x{height}")
        
        return True

    def check_channel_shell_request(self, channel):
        """Accepts shell requests to enable interactive mode."""
        
        print("[+] Shell requested")
        
        return True  # Allow the shell
    
    def check_channel_request(self, kind, chanid):
        print(f'[+] Channel {kind} requested')

        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED

    def check_auth_publickey(self, username, key):
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username):
        return 'password,publickey'         

    def check_channel_exec_request(self, channel, command):
        # This is the command we need to parse
        print(command)
        self.event.set()
        return True

hostname = '0.0.0.0'
port = 2222

def handle_client(chan: paramiko.Channel):
    """Handles interactive SSH command execution."""
    chan_buffer = ChannelBuffer(channel=chan)
    chan_buffer.write("Welcome to Simulated Device CLI")

    while True:
        try:
            command = chan_buffer.read()
            
            if not command:
                break
            else:
                # ! Custom commands
                response = process_command(command)

                # ! Exit CMD
                if response == 'terminate':
                    chan_buffer.close()
                    sys.exit()
                    
                    break

                chan_buffer.write(response)
        except Exception:
            traceback.print_exc()
            break

def process_command(command: str):
    """Processes CLI commands and returns appropriate responses."""

    device_parser = JsonParser(filename='XS1234.json')

    # commands = {
    #     "show version": "Simulated Device v1.0\r\nOS: CustomOS",
    #     "show ip": "IP Address: 192.168.1.1\r\nSubnet Mask: 255.255.255.0",
    # }

    return device_parser.get_command(user_cmd=command)

def listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((hostname, port))

    print(f'[+] Socket listening at {hostname}:{port}')
    sock.listen(100)
    client, addr = sock.accept()

    transport = paramiko.Transport(client)
    # t.set_gss_host(socket.getfqdn(""))
    # t.load_server_moduli()
    transport.add_server_key(host_key)

    server = SSHServer()
    transport.start_server(server=server)
    chan = transport.accept(20)  # Wait for a channel

    if chan is None:
        print("[-] No channel opened, closing connection.")
        # continue

    # TODO: Add threads to allow multiple clients
    handle_client(chan=chan)

    # Wait 30 seconds for a command
    # server.event.wait(30)
    transport.close()

while True:
    try:
        listener()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as exc:
        logger.error(exc)