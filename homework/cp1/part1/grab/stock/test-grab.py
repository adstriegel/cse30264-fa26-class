# This is a super bare bones tester.

import argparse
import socket
import sys
import hashlib

# Retrieve a MD5 hash of the file content
def get_md5(filename):
   hash_object = hashlib.md5()
   with open(filename, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
         hash_object.update(chunk)
   return hash_object.hexdigest()

parsedArgs = argparse.ArgumentParser(description='Python server for GRAB server')
parsedArgs.add_argument('Server', type=str, help='Hostname or IP address of server', default='127.0.0.1')
parsedArgs.add_argument('Port', type=int, help='Port for the server', default=54000)
parsedArgs.add_argument('File', type=str, help='Filename for the request', default='data/F001.dat')
parsedArgs.add_argument('Auth', type=str, help='Auth token', default='AuthSimple')
args = parsedArgs.parse_args()

print('*********** Round 1 *******************')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.connect((args.Server, args.Port))
   s.sendall(b"INFO data/F001.dat AuthSimple")
   data = s.recv(1024)
   print(f"Received {data!r}")

   RcvData = data.decode()
   RcvInfo = RcvData.split(" ")

   # Error checking might be good so I have heard
   print(f'File: {RcvInfo[2]} -- Size: {RcvInfo[3]} -- MD5: {RcvInfo[4]}')
   ExpectedSize = RcvInfo[3]
   ExpectedMD5 = RcvInfo[4]

   s.sendall(b"GRAB data/F001.dat AuthSimple")

   data = s.recv(1024)
   print(f"Received {data!r} containing {len(data)} bytes")

   # What are we expecting?
   ExpectedResponse = "GRAB-RESP OK data/F001.dat "
   print(f' Expecting {len(ExpectedResponse)} bytes')

   if len(data) != len(ExpectedResponse):
      print(f'Hmmm - not the expected number of bytes - bail out')
      sys.exit(-1)

   # This is cheating a bit since this is human readable but we do know that
   CompString = data.decode()

   if ExpectedResponse != CompString:
      print('Did not get the expected response - bailing out')
      sys.exit(-1)
   else:
      print('Nice - we got the expected response')

   RemainingSize = int(ExpectedSize)

   # Open up a test file
   with open("test.dat", "wb") as f:
      while RemainingSize > 0:
         data = s.recv(4096)
         RemainingSize -= len(data)
         print(f' Received {len(data)} bytes -> {RemainingSize} bytes remaining')
         f.write(data)

   print('Done - Checking the MD5')

   md5 = get_md5("test.dat")

   md5string = str(md5)

   if md5string != ExpectedMD5:
      print(f'Oh no - they are different {md5string} (rcvd) vs. {ExpectedMD5} (info)')
   else:
      print('All good - It works!')

print('*********** Round 2 *******************')

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   s.connect((args.Server, args.Port))
   s.sendall(b"INFO data/FB001.dat BinaryFilePNG")
   data = s.recv(1024)
   print(f"Received {data!r}")

   RcvData = data.decode()
   RcvInfo = RcvData.split(" ")

   # Error checking might be good so I have heard
   print(f'File: {RcvInfo[2]} -- Size: {RcvInfo[3]} -- MD5: {RcvInfo[4]}')
   ExpectedSize = RcvInfo[3]
   ExpectedMD5 = RcvInfo[4]

   s.sendall(b"GRAB data/FB001.dat BinaryFilePNG")

   data = s.recv(1024)
   print(f"Received {data!r} containing {len(data)} bytes")

   # What are we expecting?
   ExpectedResponse = "GRAB-RESP OK data/FB001.dat "
   print(f' Expecting {len(ExpectedResponse)} bytes')

   if len(data) != len(ExpectedResponse):
      print(f'Hmmm - not the expected number of bytes - bail out')
      sys.exit(-1)

   # This is cheating a bit since this is human readable but we do know that
   CompString = data.decode()

   if ExpectedResponse != CompString:
      print('Did not get the expected response - bailing out')
      sys.exit(-1)
   else:
      print('Nice - we got the expected response')

   RemainingSize = int(ExpectedSize)

   # Open up a test file
   with open("test.dat", "wb") as f:
      while RemainingSize > 0:
         data = s.recv(4096)
         RemainingSize -= len(data)
         print(f' Received {len(data)} bytes -> {RemainingSize} bytes remaining')
         f.write(data)

   print('Done - Checking the MD5')

   md5 = get_md5("test.dat")

   md5string = str(md5)

   if md5string != ExpectedMD5:
      print(f'Oh no - they are different {md5string} (rcvd) vs. {ExpectedMD5} (info)')
   else:
      print('All good - It works!')
