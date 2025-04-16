from server.SSHServer import SSHServer
from server.TelnetServer import TelnetServer
from parser.JsonParser import JsonParser


if __name__ == "__main__":
    if False:
        ssh_server = SSHServer(port=2222)
        ssh_server.start()
    else:
        telnet_server = TelnetServer()
        telnet_server.start()