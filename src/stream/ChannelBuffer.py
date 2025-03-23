from paramiko import Channel

class ChannelBuffer():
    RETURN_KEY = b'\x7f'

    LINUX_EOL = '\r'
    WIN_EOL = '\r\n'

    DECODING = 'utf-8'

    def __init__(self, channel: Channel):
        self.channel = channel

    def read(self, eol=LINUX_EOL):
        """Read data from the channel until a EOL is detected"""
        line: str = ''

        while True:
            # Read one BYTE at a time
            raw_chunk: bytes = self.channel.recv(1)

            # Display on terminal
            self.write_raw(raw_data=raw_chunk)

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
    
    def write_raw(self, raw_data: str):
        """Write to the channel (live on the terminal) without adding the eol"""
        print(f'Write to channel: {raw_data}')

        self.channel.send(raw_data)

    def write(self, message: str):
        """Write to the channel adding the eol"""
        self.channel.send(self.WIN_EOL)
        self.channel.send(message)
        self.channel.send(f"{self.WIN_EOL}>")
    
    def close(self):
        """Display an exit message and close the channel"""
        self.write('Goodbye!')

        self.channel.close()
