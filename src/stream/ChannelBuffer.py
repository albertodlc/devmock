from paramiko import Channel
from stream.ChannelWrapper import ChannelWrapper
from telnetlib3.stream_writer import TelnetWriterUnicode
from telnetlib3.stream_reader import TelnetReaderUnicode

class ChannelBuffer():
    RETURN_KEY = b'\x7f'

    LINUX_EOL = '\r'

    DECODING = 'utf-8'

    def __init__(self, channel_ssh: Channel = None, reader: TelnetReaderUnicode = None, writer: TelnetWriterUnicode = None):
        if channel_ssh != None:
            self.channel: ChannelWrapper = ChannelWrapper(channel=channel_ssh)
        else:
            self.channel: ChannelWrapper = ChannelWrapper(reader=reader, writer=writer)
    async def read(self, eol=LINUX_EOL):
        """Read data from the channel until a EOL is detected"""
        line: str = ''

        while True:
            # Read one BYTE at a time
            raw_chunk: bytes = await self.channel.recv()

            # Display on terminal
            self.echo(raw_data=raw_chunk)

            # Decode chunk
            chunk: str = raw_chunk.decode(self.DECODING)

            # Connection closed
            if not chunk:
                break
            # TODO: Delete characters
            elif len(line) > 0 and chunk == self.RETURN_KEY.decode(self.DECODING):
                line = line[:-1]
                break
            
            line += chunk

            # Stop at newline
            if chunk == eol:
                print(f'Complete command: {line}')
                break
                
        return line.strip()
    
    def echo(self, raw_data: str):
        """Write to the channel (live on the terminal) without adding the eol"""
        print(f'Write to channel: {raw_data}')

        self.channel.echo(raw_data)

    def write(self, message: str):
        """Write to the channel adding the eol"""
        self.channel.send(message)
    
    def close(self):
        """Display an exit message and close the channel"""
        # self.write('Goodbye!')

        self.channel.close()
