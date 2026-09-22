# Prompts - Server Code Generation

## Prompt

Write a Python script named serve-grab.py that implements that grab server as described in this assignment.  The code should being well commented and verbose in its output to assist students in troubleshooting their output.

The various files that will be served up can be found here: https://github.com/adstriegel/cse30264-fa26-class/tree/main/homework/cp1/part1/grab

The Python code should expect two required arguments, the port number that it should listen to as a TCP server and the input JSON that lists the filenames and the accompanying authorization tokens.

Upon startup, the code should ensure that the files can be found, extract the size for each of the respective files, as well as the MD5 for each of the files.

Put the resulting script and README in the Claude working directory.  Write a test client in Python that confirms operation using localhost that will be provided to the stude
