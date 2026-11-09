# Coding Project 1 - Part 3

For Part 3, you will working with multiple clients and proposing various features.  There is a mandatory part of this project and the proposed feature part.

| **Due Date** | **Part / Description** |
|---|---|
| 11-04-26 | Part 2 - Dispatch + Work |
| 11-18-26 | Part 3 - Multiple Clients, Group-Proposed Features |

## Mandatory Portion - Part 3 [10 pts]

For the mandatory portion, you are asked to make the following modifications to your code:

* Add in an optional argument (`--maxfiles N`) to your server that gives no more than `N` files to any client.
   * Restrict the number of files by limiting the list of files given in `CLRTOSCAN`
   * Select the files in a randomized manner from the overall list of files
   * The default (unspecified) value should be a sufficiently high value (1000).

For each of the following cases, use `set5.txt` (or `set3.json`) and a `--maxfiles 2` argument.

* Start / confirm that you can connect two full-clients operating at the same time.  Note that you will likely want to run them in separate directories.

* Start / confirm that you can run your code with the server from Part 2 on a different student machine than the machine where you run one of the clients

* Create a `set6.txt` or `set4.json` file using the public IP of one of the student machines. Test that everything works if you run the `grab-server` on that machine.

Include in a `README-Part3-Mandatory.md` file any notes related to your testing and confirmation that you have completed the test.

## Group-Defined Portion - Part 3 [15 pts]

For the group-defined portion, you should select an appropriate number of features with a degree of difficult proportional to your group size.  In short, more features should be proposed or implemented relative to the size of your group.  A rough rule of thumb is that you should have at least one reasonable feature per group member (e.g. a group of one just needs one reasonable effort for the feature).

For instance, consider the following enhancements:

* Modify your server from Part 2 and full client to use a proper authentication.  For instance, is there something with public / private keys or hashing?
* Complete the same approach for `grab-server` and `grab-client`
* Modify `full-client` to push status updates to an MQTT server
   * Information on the MQTT server (login / password) can be found on Canvas
   * Select a channel with a clever name to distinguish your system
* Augment any of the servers to do the same thing
* Write a MQTT client that subscribes to your channel(s)
   * Display key results or updates
   * Augment this to provide the information inside of a Flask server for a dashboard
* Provide a set of utility shell scripts that allow you to query your server from Part 2
   * Provide a list of all recent clients and when they were last connected
   * Provide the ability to change the password for a client
* Provide a set of utility scripts that use the server to control clients
   * Tell the client to clear its cache after the next job is complete
   * Tell the client to exit after the next round of processing
* Write the underlying C code to do a comparison to determine the amount of redundancy or overlap between the two files (or find an existing utility / library to assist)
* Add in various protections
   * Restrict any of the servers to only allow hosts from certain ranges of IP addresses
   * Create a ban list to specifically disallow certain IP addresses
   * Disallow the backdoor mechanism or allow it from only certain IP addresses
* Add in various logging features
   * Record where various hosts connected from

You may also propose appropriate features of your own choosing as you see fit (console, background threads, etc.).

Describe your features and what you have implemented in the `README-Part3-Group.md` file.

## Notes

* Everyone should be contributing to each part of the project which means commits of a reasonable size from all group members.  One evaluation item (homework) near the end will be to share an evaluation of your fellow group members and their respective contributions.

* You do have some design freedom if something is not well defined.  State any key assumptions you are making in your `README-Part3.md` file.

* All commits should start with `cp1-part3` as part of their commit message.

* Generally, things will work best when you are on campus for testing.  While the VPN can be pretty solid for making you appear on campus, some things can sometimes act a bit weird.  Similarly, make sure you are on `eduroam` when working and are not on `nd-guest`.

* Remember, the CSE student machines are used for all CSE classes.  Try to not save things to the last minute lest you get caught in the cross hairs of a fellow student fork bombing a machine. Starting early also gives you the ability to ask clarifying questions as needed.

## Submission

Same mechanism as Parts 1 and 2.

Complete the following tasks to submit:

* Make sure you have a `README-Part3.md` with any caveats or important notes for grading.
   * You should also have a `README-Part3-Group.md` and `README-Part3-Mandatory.md` file.
   * You should also be submitting either `set6.txt` or `set4.json` file.
* Create a final commit with the message `cp1-part3 SUBMISSION`.
* Push your commit to your repository.
* Submit the hash (full or shortened) to the text box via Canvas.
