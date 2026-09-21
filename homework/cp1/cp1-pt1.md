# Coding Project 1 - Part 1

The focus of Coding Project 1 is to give you a project of reasonable complexity split into appropriate size parts.  Parts 1 and 2 focus on the "guts" of networking protocols and system calls interactions while crossing languages (Python and C). Part 1 focuses on a hybrid file transfer protocol over TCP.  Part 2 brings in a UDP-based dispatcher. In Part 3, you will be asked to add features commensurate with your group size to the overall system.

| **Due Date** | **Part / Description** |
| 10-04-26 | Part 1 - Grab Client |
| 11-01-26 | Part 2 - Dispatch + Work |
| 11-15-26 | Part 3 - Multiple Clients, Group-Proposed Features |

## Project Origin Story

You have recently accepted a job at a computer security firm and are tasked with working with one of the senior researchers.  The senior researcher has a brilliant history and is responsible for several of the foundational patents that the company was built on.  Unfortunately, the senior researcher no longer likes to code nor likes to use AI but that is beside the point. Hence, your assignment to the senior researcher as a support programmer.

The senior researcher has the following epiphany: "With AI being so prevalent, I think we can use the similarity between network objects (web, e-mail attachments) to establish a risk score and intercept new malicious attacks. Basically, if they are too similar and too prevalent, we use that as a feature for further investigation."

The senior researcher recalls an old API for the security gateway that was largely decommissioned but could help test out a few hypotheses. The senior researcher digs up the a sparsely worded README and notes from a past intern. At first glance, this API / protocol (`SCANGRAB`) seems to be a hybrid mishmash of HTTP-like commands and binary streaming. Commands are fully ASCII readable but instead of MIME-encoding the content, raw binary streams are inserted.  The system is architected such that a worker will register with a dispatcher running on the gateway, request a task (file to scan), grab the file, do the analysis, and then report that analysis back to the dispatcher. The senior researcher recalls that the protocol is fairly lax in its operation and thinks that the protocol could be adapted where the worker could just take on multiple objects and then scan them all together looking at similarity.

**Note:** *The README / notes are written up for both the dispatch part and the grab part.  For Part 1, we will be focusing only on the grab part but the dispatch part is provided to help you understand the bigger picture of the system.*

### Dispatch / Scan

A worker will register with the dispatch server.  Workers will get the list of objects to be scanned and should operate on the files ideally in a FIFO basis.

* A worker sends a HELLO message to the dispatcher to be authorized for doing work.  The HELLO message should be sent over UDP and formatted as `HELLO ID AUTH` where `ID` is the unique identifier (string) of the worker and `AUTH` is some sort of an authorization token that was never enabled. The `ID` must be a contiguous string and there should be a space between the `ID` and `AUTH`.  To skip authentication for testing, set `AUTH` to `AuthTestOnly39#`.

* The dispatcher (server) should respond back with `RHELLO STATUS ID` where `STATUS` is string (no spaces) and `ID` is the same ID as provided. `STATUS` is typically `OK` if all goes well.  There are also notes that a worker should periodically re-authenticate ever five minutes but no notes if that was actually put into place.

* When the worker is ready to do work (scan a file), it should send a `RDYTOSCAN ID` message to the dispatcher where `ID` is the same as from the `HELLO`. The dispatcher will respond with `CLRTOSCAN X` where `X` is the number of files in the scanning queue. The list of files follows starting with `START-LIST`, followed by each file and the server where the file can be fetched from (hostname, port) and a different authorization token (one specific for each file).  The list is finished with `END-LIST`.

* The worker sends a `SCANNING ID FILE` message where `FILE` is the `FILE` being scanned by the worker for any security issues. The dispatcher responds with `RSCANNING STATUS ID FILE` back to denote that the message has been received. There are notes that the server should allow no more than two workers at a time to work on a file but that is marked with `TBA`.

* The worker should grab that file from the *grab* server. Network objects have been saved into uniquely enumerated files by the security gateway and may be available across one or more *grab* servers.

* The worker should analyze the file (network object) for any security issues.

* The worker sends a `SCANRESULT ID FILE RESULT` message where `RESULT` is a short summary status code of the scan (`SAFE`, `HOLD`, `QUARANTINE`).  The report in human readable text should be demarcated by a `REPORT` and `REPORT-END` set of delimiters and should fit within one UDP message. The server should save the result and respond with `RSCANRESULT STATUS ID FILE RESULT` to acknowledge the receipt of the result and remove the file from the scanning list.

The senior researcher remembers that there was never a check built in as to how many objects that a worker reserve.  There may or may not be a timer but hopefully, that will not come into play.

**Note:** As we have discussed in class, many network protocols have behaviors that are specifically defined and often many grey areas where things are not explicitly forbidden.  It is this grey area that the project is going to take advantage of by issues multiple `SCANNING` requests.

**Note 2:** The dispatch system is for Part 2.  This is strictly for background information on how the system works.

### Grab System

The grab part of `SCANGRAB` is a hybrid system blending human readable text and binary streaming.  Whereas the dispatch system is UDP-based, the *grab* system is TCP-based.

* Each file is fetched by connecting to the grab server on the specified port. The client can either send a `INFO` command or a `GRAB` command. The `INFO` command provides information about a particular file (size, checksum) while the `GRAB` command fetches the actual content.

* The `INFO` command should be sent as `INFO FILE AUTH` where `FILE` is the name of the file to grab and `AUTH` is the authorization token to get access to the file.

* The grab server should send back `INFO-RESP STATUS FILE SIZE MD5` where `STATUS` is a string denoting the status, `FILE` is the name of the file, `SIZE` is the size of the file in bytes, and `MD5` is the MD5 checksum for the file.

* The `GRAB` command should be sent `GRAB FILE AUTH` where `FILE` is the name of the file to grab and `AUTH` is the token associated with that file.

* The response will be sent back as `GRAB-RESP STATUS FILE` where `STATUS` will be `OK` followed by the file name, a single space, and the binary content of the file.  Otherwise, the status code will be a string followed by a potentially longer explanation.

**Note:** The grab client is what you will be writing for the first part of the coding project.

### State of the Code

The past intern had implemented a vibe-coded prototype in Python and got a few things working including a rough sketch of the message flow for testing.  Unfortunately, the worker code was lost in a terrible `rm -rf` incident in the client directory before the repository was pushed on the last day of the summer.

The intern had the following notes for the dispatch:

```
Working Dispatch Exchange to Dispatch at Port 54105

C->S|HELLO Striegel-Test AuthTestOnly39#

S->C|RHELLO OK Striegel-Test

C->S|RDYTOSCAN Striegel-Test

S->C|CLRTOSCAN 2
     START-LIST
     F001.dat 127.0.0.6 54100 SweetAuth
     F002.dat 127.0.0.6 54100 AuthSet22x7
     END-LIST

C->S|SCANNING Striegel-Test F001.dat
S->C|RSCANNING OK Striegel-Test F001.dat

C->S|SCANRESULT Striegel-Test F001.dat SAFE
S->C|RSCANRESULT OK Striegel-Test F001.dat SAFE
```

And for the grab server:

```
Open up a new connection to the file grab server (GS=127.0.0.6:54100)

C->GS|INFO F001.dat SeetAuth
GS->C|INFO-RESP WRONGAUTH F001.dat

C->GS|INFO F001.txt SweetAuth
GS->C|INFO-RESP WRONGAUTH F001.dat

C->GS|INFO F001.dat SweetAuth
GS->C|INFO-RESP OK F001.dat xxxxx (long MD5)

C->GS|GRAB F001.dat SweetAuth
S2->C|GRAB-RESP OK F001.txt HelloWorld--!--
```

The senior researcher does a double check of the code and grimaces a bit, remembering the lost worker code.  After a small bit of searching, the researcher finds the prototype Dispatcher code and Grab server code, both written in Python.

## Task - Part 1

For Part 1, your task is to write the grab client as well as a bit of helper code around the grab client.

* Write C code to create an executable named (`cgrab`) that takes in four parameters, the name of the file, the hostname / IP address of the grab server, the port number for the grab server, and the authorization token to use.
   * You will likely want to use the `INFO` command first to help you out with knowing the size of the file that will be transferred.  It is possible to do it without it, just not advisable.
   * Remember the formatting of the packets and commands.
   * If the file is successfully downloaded, it should be saved to a sub-directory named `scans`. If needed, that directory should be created. In the event that the file already exists, it should be overwritten by default without prompting.

* Write a shell script (`batchgrab`) that does the following: (1) Opens a file (input argument) that contains the results of a `CLRTOSCAN` response, one file per line; (2) Iterate through each item and fetch each file.

* It is up to you if you want to make use of the `MD5` checksum to verify things.  It might not be a bad idea to do that manually to ensure that things have been properly downloaded.

* There are multiple example files for the shell script that are present in the class repository. You will likely need to modify them to use an appropriate port number for your group (see later) as well as potentially modify the IP addresses depending on where you are testing your client. The examples can be found in `cp1/part1/dispatch/clrtoscan`. Note that `set4.txt` adds in comments and one bad authorization into the mix.

* Make sure to have an appropriate `.gitignore` to avoid including objects or the compiled binary.

## Provided Code

Code will be provided for the `grab` server in the class repository.  The `dispatch` server code will be shared shortly as well but it is not needed at this stage.  All of the server code will be written in Python.  You are welcome to add in additional debugging outputs to the Python code or to request that the code be modified to be slightly more verbose.

You should generally be in the habit of doing a fresh pull from the repository at the start of each coding session. See the `README.md` and code itself for instructions on how to start the respective Python code.

A few other notes:

* You will be assigned a set of port numbers that are listed on Canvas.  These are port numbers that are exposed to machines on campus from the CSE student machines.

* Your code will need to eventually run on the student machine but you can do your initial testing on your own machine provided that the CSE student machines are accessible.

## Structure

You should have a `cp1` directory present in your shared repository.  Your `Makefile` and `batchgrab` files should be present here. Your `Makefile` should create `cgrab` in that same directory.

You should also have a `README.md` with appropriate information.

## Notes

* Everyone should be contributing to each part of the project which means commits of a reasonable size from all group members.  One evaluation item (homework) near the end will be to share an evaluation of your fellow group members and their respective contributions.

* All commits should start with `cp1-part1` as part of their commit message.

* Generally, things will work best when you are on campus for testing.  While the VPN can be pretty solid for making you appear on campus, some things can sometimes act a bit weird.  Similarly, make sure you are on `eduroam` when working and are not on `nd-guest`.

* Remember, the CSE student machines are used for all CSE classes.  Try to not save things to the last minute lest you get caught in the cross hairs of a fellow student fork bombing a machine. Starting early also gives you the ability to ask clarifying questions as needed.

## Submission

Complete the following tasks to submit:

* Make sure you have a `README.d` with any caveats or important notes for grading.
* Create a final commit with the message `cp1-part1 SUBMISSION`.
* Push your commit to your repository.
* Submit the hash (full or shortened) to the text box via Canvas.

## Rubric

To be added - each part will be worth 25 points

Each part is equally weighted though different in difficulty.  As you are just learning how to write socket code and more approrpiately debug socket code, this part will have *less* to do compared to Part 2 and Part 3.