from paramiko import Channel
from telnetlib3.stream_writer import TelnetWriterUnicode
from telnetlib3.stream_reader import TelnetReaderUnicode

class ChannelWrapper():
    isSsh: bool = False
    DECODING = 'utf-8'

    RETURN_KEY = b'\x7f'

    LINUX_EOL = '\r'
    WIN_EOL = '\r\n'

    def __init__(self, channel: Channel = None, reader: TelnetReaderUnicode = None, writer: TelnetWriterUnicode = None):
        if channel != None:
            self.isSsh = True
            self.channel = channel
        else:
            self.isSsh = False
            self.reader = reader
            self.writer = writer
    def send(self, raw_data: str):
        '''
        Send a command
        '''
        if self.isSsh:
            self.channel.send(self.WIN_EOL)
            self.channel.send(raw_data)
            self.channel.send(f"{self.WIN_EOL}>")
        else:
            self.writer.write(self.WIN_EOL)
            self.writer.write(raw_data)
            self.writer.write(f"{self.WIN_EOL}>")
    
    def echo(self, raw_data):
        if self.isSsh:
            self.send(raw_data)
        else:
            # TODO: Improve this (avoid encoding/decoding multiple times)
            chunk: str = raw_data.decode(self.DECODING)
            self.writer.echo(chunk)

    async def recv(self) -> str:    
        if self.isSsh:
            return self.channel.recv(1)
        else:
            # TODO: Improve this (avoid encoding/decoding multiple times)
            decoded_data = await self.reader.read(1)
            
            # Default is UTF-8
            byte_data = decoded_data.encode()

            return byte_data

    def close(self):
        if self.isSsh:
            self.channel.close()
        else:
            self.writer.close() 
            # TODO: Reader must be closed?