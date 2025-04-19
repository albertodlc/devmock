from server.SSHServer import SSHServer
from server.TelnetServer import TelnetServer

if __name__ == "__main__":
    if False:
        ssh_server = SSHServer(port=2222)
        ssh_server.start()
    else:
        telnet_server = TelnetServer(port=2323)
        telnet_server.start()