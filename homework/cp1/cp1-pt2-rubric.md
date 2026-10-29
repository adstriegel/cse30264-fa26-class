# Rubric - Coding Project 1 - Part 2

25 points maximum

* [6 pts] Code structure
   * 2 pts - Server code
   * 2 pts - Wrapper code
   * 1 pt - change-set code
   * 1 pt - Documentation / correct locations for files
* [7 pts] - Server
   * 1 pt - Properly runs on the CSE student machine
   * 1 pt - HELLO2 is parsed properly
   * 1 pt - RHELLO2 is responded properly
   * 1 pt - CLRTOSCAN is parsed properly
   * 1 pt - RDYTOSCAN is responded properly
   * 1 pt - New tokens are generated for each different client
   * 1 pt - Arguments can change port, auth file, set
* [7 pts] full-client wrapper
   * 1 pt - Properly runs on the CSE student machine
   * 1 pt - Properly catches Control-C and exits gracefully
   * 1 pt - Properly sleeps as part of the loop
   * 4 pt - Properly loops and underlying client fetches all relevant files (set1, set3, set5)
      * Ideally sets via change-set but also OK if selected on server launch
* [3 pts] change-set (script + server side)
   * 2 pts - Proper authentication, properly switches a set of files (set1 to set3)
   * 1 pt - Denies if the password is incorrect
* [2 pts] - Additional Robustness
   * 1 pt - The server is helpful on errors (ex. bad password is displayed to stdin or stderr)
   * 1 pt - The client is helpful on errors (ex. bad password is displayed to stdin or stderr)
