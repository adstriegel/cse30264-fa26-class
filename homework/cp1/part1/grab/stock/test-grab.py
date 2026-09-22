# This is a super bare bones tester.

import argparse
import socket

parsedArgs = argparse.ArgumentParser(description='Python server for GRAB server')
parsedArgs.add_argument('Server', type=str, help='Hostname or IP address of server', default='127.0.0.1')
parsedArgs.add_argument('Port', type=int, help='Port for the server', default=54000)
parsedArgs.add_argument('File', type=str, help='Filename for the request', default='data/F001.dat')
parsedArgs.add_argument('Auth', type=str, help='Auth token', default='AuthSimple')
args = parsedArgs.parse_args()

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.connect((args.Server, args.Port))
   s.sendall(b"INFO data/F001.dat AuthSimple")
   data = s.recv(1024)
   print(f"Received {data!r}")
