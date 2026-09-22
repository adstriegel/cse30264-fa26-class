#!/usr/bin/env python3
"""
server-grab.py - SCANGRAB "grab" server (CSE 30264, Coding Project 1, Part 1)

Usage:
    python3 server-grab.py PORT FILES_JSON [--host HOST] [--persistent] [--timeout SECS]

    PORT        TCP port to listen on
    FILES_JSON  JSON file listing the files to serve and their authorization
                tokens, for example:
                    [ { "File": "data/F001.dat", "Auth": "AuthSimple" },
                      { "File": "data/F002.dat", "Auth": "AFE4c3982a" } ]

Protocol (all commands / status lines are ASCII, terminated by a newline):

    C -> S   INFO FILE AUTH
    S -> C   INFO-RESP STATUS FILE SIZE MD5          (STATUS == OK)
             INFO-RESP STATUS FILE                   (STATUS != OK)

    C -> S   GRAB FILE AUTH
    S -> C   GRAB-RESP OK FILE <raw bytes of file>   (exactly ONE space, then
                                                      SIZE bytes of binary data,
                                                      no trailing newline)
             GRAB-RESP STATUS FILE explanation\\n     (STATUS != OK)

STATUS values used by this server:
    OK          request succeeded
    WRONGAUTH   the file exists but the token is not valid for it
    NOFILE      no such file on this server
    BADFORMAT   command was recognized but had the wrong number of arguments
    (an unrecognized command gets:  ERROR BADCMD explanation)

Behavior notes:
  * By default the server closes the connection after answering ONE command
    (the end of a GRAB is therefore also signalled by the close).  Use
    --persistent to allow several commands on a single connection.
  * The FILE named in a request is the *base name* (e.g. F001.dat), not the
    path listed in the JSON (data/F001.dat).  Only names present in the JSON
    can ever be served, so path tricks such as ../ cannot escape.
  * The same file may be listed several times in the JSON with different
    tokens; any one of the tokens is accepted for that file.
  * On startup every file is located, sized and MD5-hashed.  If an entry in the
    JSON is bad (file missing, malformed, unusable token) the server reports it,
    skips that entry, and carries on serving the rest.
"""

import argparse
import hashlib
import json
import os
import socket
import sys
import threading
import time

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------
MAX_LINE = 4096          # longest command line we will accept (bytes)
SEND_CHUNK = 64 * 1024   # how much of a file we read/send at a time
DEFAULT_TIMEOUT = 30.0   # seconds a client may sit idle before we hang up

# Protects interleaved print() output coming from multiple client threads
_print_lock = threading.Lock()


def log(tag, msg):
    """Timestamped, thread-safe log line, e.g.  [12:01:33.512] [conn 3] msg"""
    now = time.time()
    stamp = time.strftime("%H:%M:%S", time.localtime(now)) + ".%03d" % (int(now * 1000) % 1000)
    with _print_lock:
        print("[%s] [%s] %s" % (stamp, tag, msg), flush=True)


# ----------------------------------------------------------------------------
# Startup: load the JSON and inspect every file
# ----------------------------------------------------------------------------
def md5_of_file(path):
    """Return the hex MD5 digest of a file, read in chunks."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        while True:
            block = f.read(SEND_CHUNK)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def load_catalog(json_path):
    """
    Read the JSON file, locate each listed file, and compute its size and MD5.

    Returns a dict keyed by base file name:
        { "F001.dat": { "path": <real path>, "size": int, "md5": str,
                        "tokens": set([...]) }, ... }

    Prints a line for every entry.  A bad entry (missing file, malformed
    object, unusable token, conflicting name) is reported and SKIPPED: the
    server still starts and serves everything that was valid.  A summary of
    all skipped entries is printed at the end so they are easy to spot.
    Only a missing JSON file is fatal, since it is almost certainly a typo
    in the command line.
    """
    problems = []

    print("Reading file list from: %s" % os.path.abspath(json_path))
    try:
        with open(json_path, "r") as f:
            entries = json.load(f)
    except FileNotFoundError:
        sys.exit("ERROR: JSON file not found: %s" % json_path)
    except json.JSONDecodeError as e:
        print("  ERROR: %s is not valid JSON (%s); no files will be served" % (json_path, e))
        entries = []

    if not isinstance(entries, list):
        print("  ERROR: top level of %s must be a JSON list of {\"File\", \"Auth\"} objects; no files will be served"
              % json_path)
        entries = []

    json_dir = os.path.dirname(os.path.abspath(json_path))
    catalog = {}

    print("Found %d entries in the JSON.  Locating files, computing sizes and MD5s..." % len(entries))
    def skip(msg):
        """Report a bad entry right where it happens and remember it for the summary."""
        problems.append(msg)
        print("  SKIPPING: " + msg)

    for i, entry in enumerate(entries):
        where = "entry #%d" % (i + 1)
        if not isinstance(entry, dict) or "File" not in entry or "Auth" not in entry:
            skip("%s: must be an object with \"File\" and \"Auth\" keys (got %r)" % (where, entry))
            continue

        listed, token = str(entry["File"]), str(entry["Auth"])
        if token == "" or any(c.isspace() for c in token):
            skip("%s (%s): token %r is empty or contains whitespace, so a client could never send it"
                            % (where, listed, token))
            continue

        # Look for the file relative to the JSON file first, then the current
        # directory (or as an absolute path).
        candidates = [os.path.join(json_dir, listed), listed]
        real = next((p for p in candidates if os.path.isfile(p)), None)
        if real is None:
            skip("%s: file %r not found (looked in: %s)" % (where, listed, ", ".join(candidates)))
            continue
        real = os.path.abspath(real)

        name = os.path.basename(listed)
        if name in catalog:
            # Same name again: either another token for the same file (fine)
            # or a genuinely different file with the same name (not fine).
            if catalog[name]["path"] != real:
                skip("%s: base name %r is used by two different files; keeping the first:\n      %s\n      %s"
                                % (where, name, catalog[name]["path"], real))
                continue
            if token in catalog[name]["tokens"]:
                print("  WARNING: %s: duplicate entry for %s with token %r (ignored)" % (where, name, token))
            else:
                catalog[name]["tokens"].add(token)
                print("  %-12s additional token %r  (%s)" % (name, token, where))
            continue

        try:
            size = os.path.getsize(real)
            digest = md5_of_file(real)
        except OSError as e:
            skip("%s: cannot read %r: %s" % (where, real, e))
            continue
        catalog[name] = {"path": real, "size": size, "md5": digest, "tokens": {token}}
        print("  %-12s %9d bytes  md5=%s  token=%r" % (name, size, digest, token))
        print("  %-12s (%s)" % ("", real))

    if problems:
        print("\nWARNING: %d entr%s in %s could not be used and will NOT be served:"
              % (len(problems), "y" if len(problems) == 1 else "ies", json_path))
        for p in problems:
            print("  - " + p)
    if not catalog:
        print("\nWARNING: there are no valid files to serve; every request will get NOFILE.")

    return catalog


# ----------------------------------------------------------------------------
# Per-connection handling
# ----------------------------------------------------------------------------
def read_line(conn, buf):
    """
    Read one newline-terminated command from the socket.

    TCP is a byte stream: a command can arrive in pieces, or two commands can
    arrive together, so we keep leftover bytes in `buf` between calls.

    Returns (line_bytes_or_None, remaining_buf).  None means the client closed
    the connection (or sent an over-long line, signalled by raising ValueError).
    """
    while b"\n" not in buf:
        if len(buf) > MAX_LINE:
            raise ValueError("command line longer than %d bytes without a newline" % MAX_LINE)
        data = conn.recv(1024)
        if not data:
            return None, buf          # peer closed
        buf += data
    line, _, rest = buf.partition(b"\n")
    return line.rstrip(b"\r"), rest   # tolerate CRLF line endings


def send_line(conn, tag, text):
    """Send an ASCII status line (adds the newline) and log exactly what was sent."""
    log(tag, "SEND  %r" % (text + "\n"))
    conn.sendall((text + "\n").encode("ascii", "replace"))


def check_request(catalog, cmd, parts):
    """
    Validate a parsed INFO/GRAB request.
    Returns (status, name, entry_or_None).  status is OK / BADFORMAT / NOFILE / WRONGAUTH.
    """
    if len(parts) != 3:
        return "BADFORMAT", "-", None
    name, token = parts[1], parts[2]
    entry = catalog.get(name)
    if entry is None:
        return "NOFILE", name, None
    if token not in entry["tokens"]:
        return "WRONGAUTH", name, None
    return "OK", name, entry


def do_info(conn, tag, catalog, parts):
    status, name, entry = check_request(catalog, "INFO", parts)
    if status == "OK":
        send_line(conn, tag, "INFO-RESP OK %s %d %s" % (name, entry["size"], entry["md5"]))
    elif status == "BADFORMAT":
        send_line(conn, tag, "INFO-RESP BADFORMAT expected: INFO FILE AUTH (got %d word(s) instead of 3)" % len(parts))
    elif status == "NOFILE":
        log(tag, "DENY  no such file %r (server has: %s)" % (name, ", ".join(sorted(catalog))))
        send_line(conn, tag, "INFO-RESP NOFILE %s" % name)
    else:
        log(tag, "DENY  token %r is not valid for %s" % (parts[2], name))
        send_line(conn, tag, "INFO-RESP WRONGAUTH %s" % name)


def do_grab(conn, tag, catalog, parts):
    status, name, entry = check_request(catalog, "GRAB", parts)
    if status == "BADFORMAT":
        send_line(conn, tag, "GRAB-RESP BADFORMAT - expected: GRAB FILE AUTH (got %d word(s) instead of 3)" % len(parts))
        return
    if status == "NOFILE":
        log(tag, "DENY  no such file %r (server has: %s)" % (name, ", ".join(sorted(catalog))))
        send_line(conn, tag, "GRAB-RESP NOFILE %s no such file on this server" % name)
        return
    if status == "WRONGAUTH":
        log(tag, "DENY  token %r is not valid for %s" % (parts[2], name))
        send_line(conn, tag, "GRAB-RESP WRONGAUTH %s authorization token rejected" % name)
        return

    # Header: "GRAB-RESP OK <name> " -- note the single trailing space, and no newline.
    header = ("GRAB-RESP OK %s " % name).encode("ascii")
    log(tag, "SEND  %r  (followed by %d bytes of file data)" % (header, entry["size"]))
    conn.sendall(header)

    sent = 0
    with open(entry["path"], "rb") as f:
        while True:
            block = f.read(SEND_CHUNK)
            if not block:
                break
            conn.sendall(block)
            sent += len(block)
    log(tag, "SENT  %d of %d expected file bytes (%d bytes on the wire including header)"
        % (sent, entry["size"], sent + len(header)))
    if sent != entry["size"]:
        log(tag, "WARNING: the file changed on disk since startup; the size/MD5 reported by INFO are now stale")


def handle_client(conn, addr, conn_id, catalog, persistent, timeout):
    """Serve one client connection (runs in its own thread)."""
    tag = "conn %d" % conn_id
    log(tag, "OPEN  connection from %s:%d" % addr)
    conn.settimeout(timeout)
    buf = b""
    commands = 0
    try:
        while True:
            try:
                line, buf = read_line(conn, buf)
            except ValueError as e:
                log(tag, "ERROR %s - closing" % e)
                send_line(conn, tag, "ERROR BADCMD %s" % e)
                break
            except socket.timeout:
                log(tag, "TIMEOUT no complete command within %.0f s (did your command end with a newline?) - closing" % timeout)
                break
            if line is None:
                log(tag, "CLOSE client closed the connection%s"
                    % ("" if commands else " without sending a command"))
                if buf:
                    log(tag, "      (discarding %d unterminated byte(s): %r -- commands must end with a newline)" % (len(buf), buf))
                break

            commands += 1
            log(tag, "RECV  %r" % (line + b"\n"))
            text = line.decode("ascii", "replace")
            parts = text.split()

            if not parts:
                send_line(conn, tag, "ERROR BADCMD empty command")
            elif parts[0] == "INFO":
                do_info(conn, tag, catalog, parts)
            elif parts[0] == "GRAB":
                do_grab(conn, tag, catalog, parts)
            else:
                log(tag, "DENY  unknown command %r (valid: INFO, GRAB; commands are case-sensitive)" % parts[0])
                send_line(conn, tag, "ERROR BADCMD unknown command %s (expected INFO or GRAB)" % parts[0])

            if not persistent:
                break
    except (BrokenPipeError, ConnectionResetError) as e:
        log(tag, "ERROR client went away mid-conversation: %s" % e)
    except socket.timeout:
        log(tag, "TIMEOUT while sending - closing")
    except Exception as e:  # never let one bad client kill the server
        log(tag, "ERROR unexpected %s: %s" % (type(e).__name__, e))
    finally:
        try:
            conn.close()
        except OSError:
            pass
        log(tag, "DONE  connection closed (%d command(s) handled)" % commands)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="SCANGRAB grab server (TCP)")
    ap.add_argument("port", type=int, help="TCP port to listen on")
    ap.add_argument("files_json", help="JSON file listing File / Auth pairs")
    ap.add_argument("--host", default="", help="address to bind (default: all interfaces)")
    ap.add_argument("--persistent", action="store_true",
                    help="allow multiple commands per connection instead of closing after one")
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                    help="idle timeout per connection in seconds (default %(default)s)")
    args = ap.parse_args()

    if not (0 < args.port < 65536):
        sys.exit("ERROR: port must be between 1 and 65535")

    catalog = load_catalog(args.files_json)

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((args.host, args.port))
    except OSError as e:
        sys.exit("ERROR: cannot bind to %s:%d - %s (is another server already using this port?)"
                 % (args.host or "0.0.0.0", args.port, e))
    srv.listen(16)

    print("\nServing %d file(s): %s" % (len(catalog), ", ".join(sorted(catalog))))
    print("Listening on %s:%d (%s).  Press Ctrl-C to stop.\n"
          % (args.host or "0.0.0.0", args.port,
             "multiple commands per connection" if args.persistent else "one command per connection"))

    conn_id = 0
    try:
        while True:
            conn, addr = srv.accept()
            conn_id += 1
            t = threading.Thread(target=handle_client,
                                 args=(conn, addr, conn_id, catalog, args.persistent, args.timeout),
                                 daemon=True)
            t.start()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        srv.close()


if __name__ == "__main__":
    main()
