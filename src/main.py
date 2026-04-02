# src/main.py
import sys
import os
import argparse
sys.path.insert(0, os.path.dirname(__file__))

from server.SSHServer import SSHListener
from server.TelnetServer import TelnetServer

parser = argparse.ArgumentParser()
parser.add_argument('--ssh', action='store_true')
parser.add_argument('--telnet', action='store_true')
args = parser.parse_args()

if args.ssh:
    SSHListener(port=2222).start()
elif args.telnet:
    TelnetServer(port=2323).start()