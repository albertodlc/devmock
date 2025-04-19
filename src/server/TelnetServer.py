import asyncio
import telnetlib3

from command.Commands import Commands

from stream.ChannelBuffer import ChannelBuffer
from telnetlib3.stream_writer import TelnetWriterUnicode
from telnetlib3.stream_reader import TelnetReaderUnicode

class TelnetServer:
    def __init__(self, host='0.0.0.0', port=2323):
        self.host = host
        self.port = port
        self.server = None
        self.loop = asyncio.get_event_loop()

        self.cmds = Commands('XS1234.json')

    async def shell(self, reader: TelnetReaderUnicode , writer: TelnetWriterUnicode):
        self.chan_buffer = ChannelBuffer(reader=reader, writer=writer)

        self.chan_buffer.write("Welcome to the Telnet server!\r\nType 'help', 'show ip', or 'exit'")

        while True:
            line = await self.chan_buffer.read()
            if not line:
                break

            command = line.strip().lower()

            cmd_response: str = self.cmds.process_command(command)

            if cmd_response == "terminate":
                self.chan_buffer.close()
                break
            else:
                self.chan_buffer.write(cmd_response)

    def start(self):
        '''Init server and setup the main loop'''

        print(f"Starting Telnet server on {self.host}:{self.port}")
        coro = telnetlib3.create_server(
            host=self.host,
            port=self.port,
            shell=self.shell
        )
        self.server = self.loop.run_until_complete(coro)

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())
            self.loop.close()

