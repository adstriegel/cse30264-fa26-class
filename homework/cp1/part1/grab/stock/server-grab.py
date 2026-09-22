# server-grab.py : Stock server for Coding Project 1
#
# Syntax:
#  python3 server-grab.py --port 54005 files.json
#
# --port     Optionally changes the port from 54000 to a specific value
# --server   The IP or hostname of the server, default is localhost
# --prefix   Path to pre-pend for all file listings
# --verbose  Turn on verbose mode
#
# Alternative Invocation:
#
# python3 server-grab.py --port 54005 ../files.json --prefix ../

import argparse
import sys
import os
import time
import socket
import json
import hashlib

# Retrieve a MD5 hash of the file content
def get_md5(filename):
   hash_object = hashlib.md5()
   with open(filename, "rb") as f:
      for chunk in iter(lambda: f.read(4096), b""):
         hash_object.update(chunk)
   return hash_object.hexdigest()


parsedArgs = argparse.ArgumentParser(description='Python server for GRAB server')
parsedArgs.add_argument('--port', type=int, help='Port for the server', default=54000)
parsedArgs.add_argument('FileInfo', type=str, help='JSON of all file information', default='files.json')
parsedArgs.add_argument('--server', type=str, help='Hostname or IP address of server', default='127.0.0.1')
parsedArgs.add_argument('--verbose', help='Enable verbose output', action="store_true")
parsedArgs.add_argument('--prefix', help='Path to pre-pend for all files listed', default='')
parsedArgs.add_argument('--filecheck', help='File check only', action="store_true")
args = parsedArgs.parse_args()

# Attempt to open up the file listing

print('GRAB Server - Initializing....')

try:
   # Use 'with' to ensure the file closes automatically even if errors occur
   with open(args.FileInfo, "r") as file:
      print('Opened File Info: ' + args.FileInfo)

      # Attempt to load the file
      FileData = json.load(file)

      print("  JSON Parsed ... OK")
      print("  Files Identified: " + str(len(FileData)))

except FileNotFoundError:
    print(f"Error: The file at '{args.FileInfo}' was not found.")
    sys.exit(0)

except json.JSONDecodeError as e:
    print(f"Error: Failed to parse JSON. Invalid syntax.")
    print(f"Details: {e.msg} at line {e.lineno}, column {e.colno}")
    sys.exit(0)

except PermissionError:
    print(f"Error: Permission denied to read the file at '{args.FileInfo}'.")
    sys.exit(0)

except Exception as e:
    print(f"An unexpected error occurred: {e}")
    sys.exit(0)

# Confirm that each of the files are present and figure out the size / MD5 checksum

ConfirmedList = {}

for TheFile in FileData:
   NetFilePath = args.prefix + TheFile["File"]

   print('Checking on -> ' + NetFilePath )

   # Check the size which will also confirm that we have access to the file
   try:
      TheFileSize = os.path.getsize(NetFilePath)
   except OSError as e:
      print(' OS Error ' + str(e))
      print(' Removing this file from the list')
      continue

   # Get the MD5 for the file using a system command
   theMD5 = get_md5(NetFilePath)

   TheFile["FileSize"] = str(TheFileSize)
   TheFile["MD5"] = str(theMD5)

   ConfirmedList[TheFile["File"]] = TheFile

   if args.verbose:
      print(' Confirmed access -> ' + TheFile["FileSize"] + " bytes with an MD5 of " + TheFile["MD5"])

# At this point we now have our list of "good" files
print('Properly Identified Files: ' + str(len(ConfirmedList)))

# Warn the user if there are not any "good" files to serve
if len(ConfirmedList) == 0:
   print('Warning: No files have been indexed successfully - cannot serve any files')

# Bail out if we only have a file check
if args.filecheck:
   print('File check only requested - exiting')
   sys.exit(0)

# Get going on the server itself
print('Initiating Server Socket on Port ' + str(args.port))


# Establish the socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
   # Coming at you live from any interface on the machine
   s.bind(('', args.port))

   s.listen()
   print(f"Grab Server now listening on {args.port} for new connections")

   ThePktCount = 0

   # Loop forever
   while True:
      try:
         print('Waiting for a new connection....')
         conn, addr = s.accept()

         with conn:
            print(f"Connected by {addr}")

            while True:

               data = conn.recv(1024)
               if not data:
                  break

               if args.verbose:
                  print(f"{ThePktCount} Received a read of {len(data)} from client: {data.decode()}")

               theRequest = data.decode()

               if theRequest.startswith('INFO'):
                  if args.verbose:
                     print(' -> INFO request identified')

                  theTokens = theRequest.split(' ')

                  if args.verbose:
                     print(f" -> {len(theTokens)} parts detected")

                  if len(theTokens) < 3:
                     print(f"Error: Too few parts ({len(theTokens)}) to the INFO request")
                     # Send a response back
                     theResponse = "INFO-RESP ERR-FMT"
                     conn.send(theResponse.encode('utf-8'))
                     continue
                  elif len(theTokens) > 3:
                     print(f"Warning: Too many parts ({len(theTokens)}) to the INFO request")

                  TheCommand = theTokens[0]
                  TheFileReq = theTokens[1]
                  TheAuth = theTokens[2]

                  if args.verbose:
                     print(f'--> Command: {TheCommand} len={len(TheCommand)}')
                     print(f'--> File:    {TheFileReq} len={len(TheFileReq)}')
                     print(f'--> Auth:    {TheAuth} len={len(TheAuth)}')

                  if TheCommand != "INFO":
                     theResponse = "INFO-RESP ERR " + TheFileReq + " Unknown-INFO-Command"
                     conn.send(theResponse.encode('utf-8'))
                     continue

                  if TheFileReq in ConfirmedList:
                     if ConfirmedList[TheFileReq]["Auth"] == TheAuth:
                        theResponse = "INFO-RESP OK " + TheFileReq + " " + str(ConfirmedList[TheFileReq]["FileSize"]) + " " + str(ConfirmedList[TheFileReq]["MD5"])
                        conn.send(theResponse.encode('utf-8'))
                     else:
                        print(f'Wrong Auth: Received {TheAuth} - expected {ConfirmedList[TheFileReq]["Auth"]}')
                        theResponse = "INFO-RESP WRONGAUTH " + TheFileReq
                        conn.send(theResponse.encode('utf-8'))
                  else:
                     print('Error: File not found in the list')
                     theResponse = "INFO-RESP WRONGAUTH " + TheFileReq
                     conn.send(theResponse.encode('utf-8'))
               elif theRequest.startswith("GRAB"):
                  if args.verbose:
                     print(' -> GRAB request identified')

                  theTokens = theRequest.split(' ')

                  if args.verbose:
                     print(f" -> {len(theTokens)} parts detected")

                  if len(theTokens) < 3:
                     print(f"Error: Too few parts ({len(theTokens)}) to the GRAB request")
                     # Send a response back
                     theResponse = "GRAB-RESP ERR-FMT"
                     conn.send(theResponse.encode('utf-8'))
                     continue
                  elif len(theTokens) > 3:
                     print(f"Warning: Too many parts ({len(theTokens)}) to the GRAB request")

                  TheCommand = theTokens[0]
                  TheFileReq = theTokens[1]
                  TheAuth = theTokens[2]

                  if TheFileReq in ConfirmedList:
                     if ConfirmedList[TheFileReq]["Auth"] == TheAuth:
                        theResponse = "GRAB-RESP OK " + TheFileReq + " "
                        conn.send(theResponse.encode('utf-8'))

                        NetFilePath = args.prefix + TheFileReq
                        with open(NetFilePath, "rb") as f:
                           while chunk := f.read(4096):
                              print(f'Sending a chunk of {len(chunk)} bytes')
                              conn.send(chunk)

                     else:
                        print(f'Wrong Auth: Received {TheAuth} - expected {ConfirmedList[TheFileReq]["Auth"]}')
                        theResponse = "GRAB-RESP WRONGAUTH " + TheFileReq
                        conn.send(theResponse.encode('utf-8'))
                  else:
                     print('Error: File not found in the list')
                     theResponse = "GRAB-RESP WRONGAUTH " + TheFileReq
                     conn.send(theResponse.encode('utf-8'))
      except ConnectionResetError as e:
         print('DONE - Connection Complete')
         # This is actually not a problem - just ignore it
         pass
