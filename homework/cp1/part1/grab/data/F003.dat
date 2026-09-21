# echo-server.py : Reduced version of the tracking server doing only the echo response

import socket
import sys
import argparse
import time
import math

parser = argparse.ArgumentParser(description='Tracker - Server - Echo Only')
parser.add_argument('port', type=int, help='The port number for the server')

args = parser.parse_args()

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Binding to port ' + str(args.port))

server_address = ('', args.port)
sock.bind(server_address)
print('  Success!')

while True:
   try:
      print(' Waiting for a message from the client')
      data, clientInfo = sock.recvfrom(4096)

      print('  Received a ' + str(len(data)) + ' byte message from host ' + str(clientInfo))
      print('  Message Dump: ' + ' '.join([f'{byte:02x}' for byte in data]))

      # Send a response back

      theResponse = bytearray()
      theResponse.append(6)

      # The response length is 13 bytes
      #  Status Code for the Command (0 = No Errors (Success), Non-Zero is an Error)
      #  Reflection of the nonce (32 bits)
      #  High Resolution Time (timeval)
      #     Time in Seconds (32 bits)
      #     Fractional Time in Microseconds (32 bits)
      theResponse.append(0)
      theResponse.append(13)

      if len(data) != 7:
         theResponse.append(1)
      else:
         theResponse.append(0)

      # If there is a nonce - reflect it back, otherwise reflect a zero
      if len(data) >= 7:
         # Get the nonce (32 bit random value) for reflection
         for theNonceByte in range(4):
            theResponse.append(data[3+theNonceByte])
      else:
         for theNonceByte in range(4):
            theResponse.append(0)

      # Get the current high resolution time (seconds, microseconds)
      theTime = time.time()
      print('  Time (UTC):   ' + str(theTime))

      # modf does a modulus arithmetic equivalent for floating point but it leaves the
      #  decimal portion as a floating point (< 0) value
      #
      #  Since the C high resolution time is seconds and microseconds, we need to convert
      #  this over to microseconds

      (partialSec, wholeSec) = math.modf(theTime)
      microSec = partialSec * 1000000
      print('  Time (Split): ' + str(int(wholeSec)) + '.' + str(int(microSec)))

      theByteArray = int(wholeSec).to_bytes(4, byteorder='big')
      for theByte in theByteArray:
         theResponse.append(theByte)

      theByteArray = int(microSec).to_bytes(4, byteorder='big')
      for theByte in theByteArray:
         theResponse.append(theByte)

      # Send the response
      sent = sock.sendto(theResponse, clientInfo)

      print('')

   except Exception as e:
      print(f"Error: {e}")
