# Coding Project 1 - Part 2

In Part 2, we will pivot into writing the client and server parts where you will be augmenting your C client from the first part and connecting up to a server for doing the dispatch efforts using UDP.

| **Due Date** | **Part / Description** |
|---|---|
| 11-01-26 | Part 2 - Dispatch + Work |
| 11-15-26 | Part 3 - Multiple Clients, Group-Proposed Features |

## The Story Continues

Good news, the senior researcher has been delighted with your work from the first part.  The bad news is that it turns out that the code for the dispatcher was in a worse state than the researcher had thought and you will be rewriting that code as well.  No worries, the senior researcher got permission provided that the code stays operating in the correct port range (54000 to 54150).

It also turns out that the senior researcher's memory was a bit hazy on the dispatch operation.  Some of the earlier overview was correct, other parts of it a bit less so.

After setting Claude loose to characterize the past documentation, the following notes came back:

* The dispatch server operates over UDP.

* `HELLO / RHELLO` was deprecated for a `HELLO2 / RHELLO2` message set.

* The client sends a `HELLO2` message to the server along with an `ID` but it turns out that `AUTH` actually had two parts, `AUTHMODE` and `AUTHINFO` where `AUTHMODE` was always set to `SIMPLE` and `AUTHINFO` was a string, essentially making `ID` act like a username and `AUTHMODE` act like a password.  Password checking could indeed be ignored if the `AUTHINFO` field was set to `AuthTestOnly39#`. Strong security FTW.

* The `RHELLO2` message responds with additional parts to the message `IP PORT AUTHMODE AUTHTOKEN` where `IP` was the `IP` address of the client, `PORT` was the port of the client, `AUTHMODE` is a new mode though curiously only `SIMPLE` was ever implemented and `AUTHTOKEN` is a token to use on any subsequent messages.
   * Long story short - only `RHELLO2` should be built, not `RHELLO`
   * `RHELLO` did have a `STATUS` and `ID` field reflected back
   * `RHELLO2` sends `RHELLO2 STATUS ID IP PORT AUTHMODE AUTHTOKEN`

* The `RDYTOSCAN` message and `CLRTOSCAN` were kind of close but not quite.
   * When the worker is ready to do work (scan a file), the client should send a `RDYTOSCAN ID AUTHTOKEN` message to the dispatcher where `ID` is the same as from the `HELLO` and `AUTHTOKEN` is what it got back from `RHELLO2`.
   * Instead of having a `CLRTOSCAN STATUS ID` having a `START-LIST` and `END-LIST`, it turns out that part never got built.  Instead, the `CLRTOSCAN` just includes the number of files `NUMFILES` followed by the info for each specific file (FileName, GrabServerName, GrabServerPort, AuthToken).
   * You will find that the sequence looks suspiciously like the text files in `clrtoscan`

The senior researcher has asked you to update your client to support this new functionality and to write a prototype in Python for the dispatch server while the researcher attempts to dig up the original code.

Your new Python code (`dispatch-server`) is requested to do the following:

* The server should start up taking in an argument for which port, which set of data to provide (a specific JSON file), and an authorization file.  There should be default values for each of those settings elected by you.

* Wait for UDP messages on that specific port.  It should wait for a while (one or two seconds) but not forever.

* Process the `HELLO2` message.  Confirm that the `ID` provided by the client matches up correctly using one of the auth lists.  Generate a random string (nonce) of 8-12 characters for the `AUTHTOKEN` using the same `AUTHSIMPLE` auth mode.
   * Each client should get a different `AUTHTOKEN`.  If the same ID is used, only the new `AUTHTOKEN` should work.

* Only accept `RDYTOSCAN` messages from clients that provide the correct `AUTHTOKEN` information.  The `AuthTestOnly39#` should not work on `RDYTOSCAN`, only `HELLO`.

* Using the information specified when the server started up, provide a properly formatted list.

Your enhanced client (`full-client`) should do the following:

* It should take in the IP and port of the dispatch server.  It should also take in an ID and authorization information.
   * `./full-client 127.0.0.1 54057 RandomID AuthTestOnly39#`

* On startup, it should connect to the server using that information.

* If successfully authenticated, it should send a `RDYTOSCAN` request to the server.

* If a `CLRTOSCAN` message is successfully received, it should use your code from Part 1 to fetch all of the files.

* It should pause for somewhere between ten to twenty seconds and then repeat the process.  We will swap this out in Part 3.

* You should gracefully catch and handle Control-C.

* It is up to you if this is a change to your C client or a new piece of wrapper code (Python, shell scripting, etc.).

The researcher then wants you to add a new piece of functionality to the dispatch server.

* If a `CHANGESET AUTH SetName` packet is received, it loads up the text file from the specific location to use as set information.  This should use a password of your choosing for the `AUTH` information.

Make a small Python script (`change-set`) to enable `CHANGESET`:

* Take in the server name, port number, and new set name.  Send it via the secret mechanism.

## Example Exchange

```
C->S HELLO2 GoIrishBeatStanford SIMPLE AuthTestOnly39#
S->C RHELLO2 OK GoIrishBeatStanford 127.0.0.1 32829 SIMPLE TheFoxJumps

C->S RDYTOSCAN GoIrishBeatStanford TheFoxJumps
S->C CLRTOSCAN OK GoIrishBeatStanford 1 data/F001.dat 127.0.0.1 54000 AuthSimple

15 seconds pass...

C->S RDYTOSCAN GoIrishBeatStanford TheFoxJumps
S->C CLRTOSCAN OK GoIrishBeatStanford 1 data/F001.dat 127.0.0.1 54000 AuthSimple

5 seconds pass, the CHANGESET client is run
C2->S CHANGESET SecretPwd clrtoscan/set1b.txt

22 seconds pass....

C->S RDYTOSCAN GoIrishBeatStanford TheFoxJumps
S->C CLRTOSCAN OK GoIrishBeatStanford 1 data/FB001.dat 127.0.0.1 54000 BinaryFilePNG
```

C2 is a different terminal and the secret set changing client.

## Tasks - Part 2

* Write the `dispatch-server` code in Python
* Adjust your client functionality appropriately from Part 1 augmenting it as appropriate.  You may choose best how to enhance your code
   * The easiest way is likely to write your code in Python and to invoke your C code
   * The new code should be executable as `full-client` taking the arguments as noted
   * Your client should effectively loop forever until gracefully exited via Control-C
* Add in the ability to change scanning sets via the secret back door
   * Modify the `dispatch-server` to support it
   * Create the `change-set` Python script.  It should be executable

## Structure

You should have a `cp1` directory present in your shared repository.

Everything should stay operational from Part 1.

Make a `README-Part2.md` for Part 2 information.

## Notes

* Everyone should be contributing to each part of the project which means commits of a reasonable size from all group members.  One evaluation item (homework) near the end will be to share an evaluation of your fellow group members and their respective contributions.

* All commits should start with `cp1-part2` as part of their commit message.

* Generally, things will work best when you are on campus for testing.  While the VPN can be pretty solid for making you appear on campus, some things can sometimes act a bit weird.  Similarly, make sure you are on `eduroam` when working and are not on `nd-guest`.

* Remember, the CSE student machines are used for all CSE classes.  Try to not save things to the last minute lest you get caught in the cross hairs of a fellow student fork bombing a machine. Starting early also gives you the ability to ask clarifying questions as needed.

## Submission

Same mechanism as Part 1.

Complete the following tasks to submit:

* Make sure you have a `README.d` with any caveats or important notes for grading.
* Create a final commit with the message `cp1-part2 SUBMISSION`.
* Push your commit to your repository.
* Submit the hash (full or shortened) to the text box via Canvas.

## Rubric

Rubric to be added the week before Fall Break

There is now more to do here but also more of the work is in Python.  In the last part, you will be given a bit more code but we will add in multiple clients, a dashboard, and actual analytics (you are emulating that with the random wait per set).

There will also be features that are welcome to add for part of your grade that will scale with the group size. For instance, you might ditch some of the terrible security choices and do things right or enhance the dashboard.