import argparse
import sys
import os
import time
import socket
import json
import hashlib


parsedArgs = argparse.ArgumentParser(description='Python server for GRAB server')
parsedArgs.add_argument('--port', type=int, help='Port for the server', default=54000)
parsedArgs.add_argument('FileInfo', type=str, help='JSON of all file information', default='files.json')
parsedArgs.add_argument('--server', type=str, help='Hostname or IP address of server', default='127.0.0.1')
parsedArgs.add_argument('--verbose', help='Enable verbose output', action="store_true")
parsedArgs.add_argument('--prefix', help='Path to pre-pend for all files listed', default='')
parsedArgs.add_argument('--filecheck', help='File check only', action="store_true")
args = parsedArgs.parse_args()


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.bind(('', args.port))
   s.listen()
   while True:
      try:
         conn, addr = s.accept()
         with conn:
            while True:
               data = conn.recv(1024)
               theRequest = data.decode()
               theResponse = "RESP " + theRequest
               conn.send(theResponse.encode('utf-8'))
      except ConnectionResetError as e:
         print('DONE - Connection Complete')
