from server.SSHServer import SSHServer
from parser.JsonParser import JsonParser

if __name__ == "__main__":
    ssh_server = SSHServer(port=2222)
    ssh_server.start()