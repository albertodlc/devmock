#!/usr/bin/env python
import logging
import socket
import sys
import threading
import traceback
import paramiko

from stream.ChannelBuffer import ChannelBuffer
from command.Commands import Commands

logger = logging.getLogger(__name__)


class SSHServer(paramiko.ServerInterface):
    """Paramiko SSH server interface — handles auth and channel negotiation."""

    def __init__(self):
        self.event = threading.Event()

    def check_auth_password(self, username: str, password: str) -> int:
        if username == 'admin' and password == 'admin':
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_auth_publickey(self, username: str, key) -> int:
        return paramiko.AUTH_SUCCESSFUL

    def get_allowed_auths(self, username: str) -> str:
        return 'password,publickey'

    def check_channel_request(self, kind: str, chanid: int) -> int:
        logger.debug(f'Channel requested: {kind}')
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_pty_request(self, channel, term, width, height, pixelwidth, pixelheight, modes) -> bool:
        logger.debug(f'PTY requested: {term} {width}x{height}')
        return True

    def check_channel_shell_request(self, channel) -> bool:
        logger.debug('Shell requested')
        self.event.set()
        return True

    def check_channel_exec_request(self, channel, command) -> bool:
        logger.debug(f'Exec requested: {command}')
        self.event.set()
        return True


class SSHListener:
    """Manages the SSH socket, accepts connections and spawns client threads."""

    def __init__(self, port: int = 2222, host: str = '0.0.0.0',
                 key_filename: str = None, device_cmd_filename: str = 'XS1234_TEST.json'):
        self.host = host
        self.port = port
        self.device_cmd_filename = device_cmd_filename
        self.host_key = self._load_host_key(key_filename)
        self._sock = None

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    @staticmethod
    def _load_host_key(key_filename: str | None) -> paramiko.RSAKey:
        if key_filename:
            logger.info(f'Loading host key from {key_filename}')
            return paramiko.RSAKey(filename=key_filename)
        logger.info('No key file provided — generating ephemeral RSA key')
        return paramiko.RSAKey.generate(2048)

    # ------------------------------------------------------------------
    # Client handler (runs in its own thread)
    # ------------------------------------------------------------------

    def _handle_client(self, client: socket.socket, addr: tuple) -> None:
        logger.info(f'New connection from {addr}')
        transport = None
        try:
            transport = paramiko.Transport(client)
            transport.add_server_key(self.host_key)

            server = SSHServer()
            transport.start_server(server=server)

            chan = transport.accept(20)
            if chan is None:
                logger.warning(f'No channel opened from {addr}')
                return

            # Wait for shell/exec request
            server.event.wait(10)

            commands = Commands(device_cmd_filename=self.device_cmd_filename)
            chan_buffer = ChannelBuffer(channel=chan)
            chan_buffer.write('Welcome to Simulated Device CLI')

            while True:
                command = chan_buffer.read()
                if not command:
                    break

                response = commands.process_command(command)
                logger.debug(f'CMD: {command!r} → {response!r}')

                if response == 'terminate':
                    chan_buffer.close()
                    break

                chan_buffer.write(response)

        except Exception:
            traceback.print_exc()
        finally:
            if transport:
                transport.close()
            logger.info(f'Connection closed: {addr}')

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def start(self) -> None:
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._sock.bind((self.host, self.port))
        self._sock.listen(100)
        logger.info(f'SSH server listening on {self.host}:{self.port}')

        try:
            while True:
                client, addr = self._sock.accept()
                thread = threading.Thread(
                    target=self._handle_client,
                    args=(client, addr),
                    daemon=True
                )
                thread.start()
        except KeyboardInterrupt:
            logger.info('Shutting down SSH server')
        finally:
            self._sock.close()