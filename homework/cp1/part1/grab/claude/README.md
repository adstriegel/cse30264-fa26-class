# SCANGRAB Grab Server and Test Client (CP1 Part 1)

| File | Purpose |
|------|---------|
| `server-grab.py` | The grab server (TCP). Serves files listed in a JSON file. |
| `test-grab-client.py` | Localhost test client that checks the server (and shows the protocol on the wire). |

Requires Python 3.6+ and no third-party packages.

## Running the server

```
python3 server-grab.py PORT FILES_JSON [--host HOST] [--persistent] [--timeout SECS]
```

Example (from the `grab` directory of the class repo):

```
python3 server-grab.py 54000 files.json
```

* `PORT` - TCP port to listen on (use the port assigned to your group).
* `FILES_JSON` - list of files and tokens, for example:

  ```json
  [
     { "File" : "data/F001.dat", "Auth" : "AuthSimple" },
     { "File" : "data/F002.dat", "Auth" : "AFE4c3982a" }
  ]
  ```

  File paths are resolved relative to the JSON file (then the current directory).
* `--persistent` - allow several commands per connection (default: the server answers one command, then closes).
* `--timeout` - seconds a client may be idle before the server hangs up (default 30).

**At startup** the server locates every file, records its size, and computes its MD5, printing a line for each.
A bad entry in the JSON (file not found, entry without `File`/`Auth`, a token that is empty or contains whitespace,
a name that clashes with a different file, an unreadable file) does **not** stop the server. It is reported
(`SKIPPING: entry #3: ...`), left out of the list of servable files, and summarized again just before the server starts listening.
Requests for a skipped file get `NOFILE`. If the JSON as a whole is invalid, the server reports it and serves nothing.
The only fatal startup errors are a JSON path that does not exist and a port that cannot be bound.

**While running** every connection is logged with timestamps and a connection number, showing the exact bytes received
(`RECV b'INFO F001.dat AuthSimple\n'`) and sent, plus a reason for every rejected request. If your client is misbehaving,
compare what the server says it received with what you meant to send (missing newline, extra space, wrong case, etc.).

## Protocol summary

Commands and status lines are ASCII and end with a newline (`\n`; `\r\n` is tolerated). Fields are separated by single spaces.

```
C -> S   INFO FILE AUTH
S -> C   INFO-RESP OK FILE SIZE MD5\n
         INFO-RESP STATUS FILE\n                         (on failure)

C -> S   GRAB FILE AUTH
S -> C   GRAB-RESP OK FILE <SIZE bytes of raw file data>  (on success)
         GRAB-RESP STATUS FILE explanation\n              (on failure)
```

On a successful GRAB the header is `GRAB-RESP OK FILE` followed by **one space** and then the raw bytes -
no newline after the header and none after the data. Use the `SIZE` from `INFO` to know how many bytes to read.
The server also closes the connection after the GRAB, so reading until EOF works too, but do not rely on
only that if you also need to detect a truncated transfer - compare against `SIZE` and `MD5`.

| STATUS | Meaning |
|--------|---------|
| `OK` | Success |
| `WRONGAUTH` | File exists, token is not valid for it |
| `NOFILE` | No such file on this server |
| `BADFORMAT` | Command was `INFO`/`GRAB` but did not have exactly `FILE AUTH` |
| (`ERROR BADCMD ...`) | Unrecognized command (commands are case-sensitive) |

Notes:

* `FILE` in a request is the base name (`F001.dat`), not the path in the JSON (`data/F001.dat`).
* A file may appear in the JSON several times with different tokens; any one of them works.
* Binary files are sent byte-for-byte. Your client must not treat file content as a C string (it may contain `\0`).

## Running the test client

The test client reads the same JSON file, so it knows every valid token and computes the expected size and MD5 from its local copy of the files.

Start the server yourself:

```
python3 server-grab.py 54000 files.json          # terminal 1
python3 test-grab-client.py 54000 files.json    # terminal 2
```

Or let the test start and stop the server:

```
python3 test-grab-client.py 54000 files.json --spawn
```

Add `-v` to see each command and status line. The client checks, for every file/token in the JSON: `INFO` size and MD5,
and a full `GRAB` (exact header, exact byte count, MD5 of the data, no trailing bytes). It also checks a bad token, an unknown file,
a malformed `INFO`, an unknown command, and a command that arrives one byte at a time.
It prints `PASS`/`FAIL` per check and exits non-zero if anything fails.

The test client only checks the server. To test your own `cgrab`, start the server and run `cgrab` against `localhost` and the same port,
then compare the file in `scans/` with the original, e.g. `md5 data/F001.dat scans/F001.dat` (macOS) or `md5sum` (Linux).

## Things to watch for in the provided data

* Tokens are per file: a token that is valid for one file gets `WRONGAUTH` on another. If `cgrab` gets `WRONGAUTH`, first check that
  the token in your `clrtoscan` line matches the one in `files.json` for that file (the server log prints the token it rejected).
* A file can appear in `files.json` more than once with different tokens; the server accepts any of them.
* `set4.txt` is meant to fail in places: `F004.dat` with `BooSparty!` is a bad token (`WRONGAUTH`) and `F100.dat` is an unknown file (`NOFILE`).
  Those failures are expected, and `batchgrab` should carry on to the next line.
