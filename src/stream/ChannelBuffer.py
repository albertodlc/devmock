import logging
from paramiko import Channel
from telnetlib3.stream_writer import TelnetWriterUnicode
from telnetlib3.stream_reader import TelnetReaderUnicode
from stream.ChannelWrapper import ChannelWrapper

logger = logging.getLogger(__name__)

class ChannelBuffer:
    """Buffers raw channel I/O into complete command strings.
    
    Supports both SSH (paramiko) and Telnet (telnetlib3) transports
    via ChannelWrapper abstraction.
    """

    BACKSPACE   = b'\x7f'
    CTRL_C      = b'\x03'
    EOL_UNIX    = '\r'
    EOL_WINDOWS = '\r\n'
    ENCODING    = 'utf-8'
    WELCOME_MSG = 'Welcome to Simulated Device CLI'
    EXIT_MSG    = 'Goodbye!'

    def __init__(
        self,
        channel_ssh: Channel = None,
        reader: TelnetReaderUnicode = None,
        writer: TelnetWriterUnicode = None
    ):
        if channel_ssh is not None:
            self.channel = ChannelWrapper(channel=channel_ssh)
        elif reader is not None and writer is not None:
            self.channel = ChannelWrapper(reader=reader, writer=writer)
        else:
            raise ValueError('Either channel_ssh or both reader and writer must be provided')

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def read(self, eol: str = EOL_UNIX) -> str | None:
        """Read bytes from the channel until EOL, backspace or disconnect.

        Returns the stripped command string, or None if the connection closed.
        """
        line = ''

        while True:
            raw_chunk: bytes = await self.channel.recv()

            # Connection closed
            if not raw_chunk:
                logger.info('Channel closed by remote')
                return None

            # Ctrl+C — abort current line
            if raw_chunk == self.CTRL_C:
                self._echo(raw_chunk)
                return None

            chunk = raw_chunk.decode(self.ENCODING, errors='replace')

            self._echo(raw_chunk)

            # Backspace — remove last character
            if raw_chunk == self.BACKSPACE:
                if line:
                    line = line[:-1]
                continue

            # EOL — command complete
            if chunk == eol or chunk.rstrip('\n') == eol.rstrip('\n'):
                logger.debug(f'Command received: {line!r}')
                break

            line += chunk

        return line.strip()

    def write(self, message: str) -> None:
        """Send a message to the channel appending EOL."""
        self.channel.send(message)

    def welcome(self) -> None:
        """Send the welcome banner."""
        self.write(self.WELCOME_MSG)

    def close(self) -> None:
        """Send exit message and close the channel."""
        self.write(self.EXIT_MSG)
        self.channel.close()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _echo(self, raw_data: bytes) -> None:
        """Echo raw bytes back to the terminal (local display)."""
        logger.debug(f'Echo: {raw_data!r}')
        self.channel.echo(raw_data)