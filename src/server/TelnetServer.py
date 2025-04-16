import socketserver

# Define your login credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "secret"

class TelnetHandler(socketserver.StreamRequestHandler):
    def handle(self):
        self.wfile.write(b"Welcome to the Telnet server!\r\n")
        
        # Prompt for username
        self.wfile.write(b"Username: ")
        username = self.read_line()

        # Prompt for password
        self.wfile.write(b"Password: ")
        password = self.read_line()

        # Authentication check
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            print(f'Login success for {username}')
            self.wfile.write(b"\r\nLogin successful!\r\n")
            self.interactive_shell()
        else:
            self.wfile.write(b"\r\nLogin failed. Connection closing.\r\n")

    def read_line(self):
        """
        Read a line of input from the client, removing Telnet control sequences.
        """
        raw_line = self.rfile.readline()
        print(f'RAW LINE: {raw_line}')

        cleaned_line = self.clean_telnet_data(raw_line)
        print(f'CLEANED LINE: {cleaned_line}')

        return cleaned_line

    def clean_telnet_data(self, data):
        """
        Remove Telnet control sequences (bytes starting with 0xFF)
        """
        clean_data = bytearray()

        i = 0
        while i < len(data):
            byte = data[i]

            # If we encounter IAC (0xFF), skip the next byte (Telnet control sequence)
            if byte == 0xFF:
                i += 2  # Skip IAC byte + the next byte (the command byte)
                continue
            else:
                clean_data.append(byte)

            i += 1

        # Convert the cleaned bytearray to a string (UTF-8)
        return clean_data.decode("utf-8", errors="replace").strip()

    def interactive_shell(self):
        self.wfile.write(b"Type 'exit' to disconnect.\n")
        while True:
            self.wfile.write(b"> ")
            command = self.read_line()
            if command.lower() == "exit":
                self.wfile.write(b"Goodbye!\n")
                break
            else:
                response = f"You said: {command}\n"
                self.wfile.write(response.encode("utf-8"))

class TelnetServer:
    def __init__(self, host="0.0.0.0", port=2323):
        self.host = host
        self.port = port

    def start(self):
        with socketserver.TCPServer((self.host, self.port), TelnetHandler) as server:
            print(f"Telnet server running on {self.host}:{self.port}")
            server.serve_forever()
