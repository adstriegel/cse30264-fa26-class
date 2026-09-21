# Discussion Prompt - 09-16-26 - gRPC, protobuf, web sockets

## Q: Describe to a computer science major what the importance of protobuf, web sockets, and gRPC are.

These three get lumped together because they all show up in the same architecture diagrams, but they answer three different questions: *what do the bytes mean*, *how do the bytes get there*, and *what does calling a remote thing look like in my code*.

### Protocol Buffers — the contract

Protobuf is two things at once: a schema language and a binary wire format. You write a `.proto` file declaring your message types, run a compiler, and get generated classes in Go, Java, Python, C++, whatever — with typed accessors and fast serializers.

The efficiency argument is the obvious one. JSON is self-describing text: every message carries its field names as ASCII, numbers get encoded as digit strings, and parsing means scanning for delimiters. Protobuf puts a small tag on the wire — a field *number* and a wire type — then varint-encodes integers so small values cost one byte. Nothing tells you the field is called `user_id`; you need the schema to interpret the bytes at all. Smaller, faster, and completely opaque to `curl`.

The more interesting argument is schema evolution. The field numbers are the actual contract, not the names. You can rename a field freely, add new optional fields, and old binaries that don't know about field 7 will pass it through untouched instead of choking. What you can never do is reuse a retired field number with a different type. That sounds like a fussy detail until you're running 200 services on 30 different deploy schedules, and the question "can I deploy the new consumer before the new producer?" has to have a defensible answer. Protobuf makes that answer a property of the schema rather than a matter of hoping.

The transferable lesson: defining the interface separately from any implementation of it. Same idea as CORBA IDL, Thrift, Avro, and Cap'n Proto — protobuf just won the popularity contest.

### WebSockets — breaking HTTP's request/response shape

Classic HTTP is strictly client-initiated. The server cannot say anything unless asked. For anything real-time — chat, a live price feed, a multiplayer game, a collaborative editor — that's a fundamental mismatch, and the pre-2011 workarounds were ugly: short polling (hammer the server every second, mostly to hear "nothing new"), and long polling / "Comet" (hold a request open until something happens, then immediately reopen it).

A WebSocket starts life as a normal HTTP GET carrying `Upgrade: websocket`. The server answers `101 Switching Protocols`, and from that point the same TCP connection stops speaking HTTP and becomes a bidirectional, message-oriented channel. Either side can send whenever it wants, framing overhead drops from hundreds of bytes of HTTP headers to a couple of bytes per frame, and — unlike raw TCP — you get message boundaries back, so you're not hand-rolling a length-prefix parser.

There's a nice systems lesson buried in that handshake. Technically, none of this needs to involve HTTP. It's done that way because the internet's middleboxes — corporate proxies, NAT, firewalls — had calcified around "port 443 carrying something that looks like HTTP." A protocol that opened its own port on 8081 would work on your laptop and fail in half the enterprises on earth. New transports have to disguise themselves as the old one. (QUIC does the same thing riding UDP/443.)

### gRPC — the RPC layer on top

Remote procedure call is an old idea: make invoking something on another machine look like calling a local function. Sun RPC, CORBA, DCOM, SOAP, Thrift — gRPC is the current generation, and it's basically protobuf for the interface plus HTTP/2 for the transport.

You add a `service` block to your `.proto` with method signatures, and the compiler generates both a client stub and a server interface. Implement the server side, call the client side like a local object, and the marshalling, connection handling, and dispatch are someone else's problem.

HTTP/2 is what makes it more than a faster SOAP. Because HTTP/2 multiplexes independent streams over a single TCP connection with binary framing, gRPC supports four call shapes rather than one: unary (ordinary call-and-response), server streaming (upload a query, get a stream of results), client streaming (stream telemetry up, get one acknowledgment), and fully bidirectional streaming. You also get deadline propagation, cancellation that cascades through a call chain, structured status codes, and interceptors for auth and tracing.

Its notable weakness: browsers don't expose raw HTTP/2 frames to JavaScript, so you can't call a gRPC service directly from a web page. You need grpc-web and a translating proxy. This is exactly why gRPC dominates *service-to-service* traffic inside a datacenter while REST/JSON and WebSockets still own the browser edge.

### How they fit together

Protobuf is a serialization format usable anywhere — including inside WebSocket frames, which is a common and sensible combination. WebSockets are a transport with no opinion about payload. gRPC is a full RPC framework that picks protobuf and HTTP/2 for you and adds code generation and call semantics on top.

The thing worth taking away as a CS major is where the abstraction leaks. RPC frameworks promise that a remote call looks like a local one, and that promise is a lie in ways that matter: a local call doesn't take 40ms, doesn't fail halfway with the server having already committed, and doesn't require both sides to agree on a schema written six months apart. gRPC's deadlines, explicit status codes, and cancellation semantics exist precisely because the abstraction *can't* be airtight — the framework is admitting which parts of the network you're still required to think about. Recognizing which parts of an abstraction are load-bearing and which are polite fiction is most of what makes distributed systems hard.

---

## Q: Can you give me an example of a .proto file?

Here's a ride-sharing service, which conveniently motivates all four call shapes:

```protobuf
syntax = "proto3";

package rideshare.v1;

// Generated-code options — these control the namespace of the output
// in each target language. Not part of the wire format.
option go_package = "github.com/example/rideshare/gen/v1;ridesharev1";
option java_package = "com.example.rideshare.v1";

import "google/protobuf/timestamp.proto";

// ---------- Messages ----------

message LatLng {
  double latitude  = 1;
  double longitude = 2;
}

message Rider {
  string id           = 1;
  string display_name = 2;
  // Reserved because v1 of this schema had `string home_address = 3;`
  // and we removed it. Nobody may ever reuse field 3 or the name.
  reserved 3;
  reserved "home_address";
}

enum RideStatus {
  // proto3 requires the zero value, and it should mean "unset."
  // Enum names share a namespace with the enclosing scope, hence the prefix.
  RIDE_STATUS_UNSPECIFIED = 0;
  RIDE_STATUS_REQUESTED   = 1;
  RIDE_STATUS_ASSIGNED    = 2;
  RIDE_STATUS_IN_PROGRESS = 3;
  RIDE_STATUS_COMPLETED   = 4;
  RIDE_STATUS_CANCELED    = 5;
}

message Ride {
  string id     = 1;
  Rider  rider  = 2;              // nested message
  string driver_id = 3;

  LatLng pickup      = 4;
  LatLng destination = 5;

  RideStatus status = 6;

  google.protobuf.Timestamp requested_at = 7;
  google.protobuf.Timestamp completed_at = 8;

  repeated LatLng route = 9;      // a list

  map<string, string> metadata = 10;  // app_version, promo_code, etc.

  // Exactly one of these may be set — the wire encoding guarantees that
  // setting one clears the others.
  oneof payment {
    CardPayment card   = 11;
    string      cash   = 12;
    string      credit_id = 13;
  }

  // Explicitly optional so the generated code exposes has_fare_cents(),
  // letting you distinguish "zero fare" from "fare not yet computed."
  optional int32 fare_cents = 14;
}

message CardPayment {
  string last_four   = 1;
  string brand       = 2;
  uint32 expiry_year = 3;
}

// Request/response wrappers. Even for trivial calls, wrap arguments in a
// message — you can add fields later without changing the signature.
message GetRideRequest  { string ride_id = 1; }

message WatchRideRequest { string ride_id = 1; }
message RideUpdate {
  RideStatus status   = 1;
  LatLng     position = 2;
  google.protobuf.Timestamp at = 3;
}

message TelemetryPoint {
  LatLng position   = 1;
  float  speed_mps  = 2;
  float  heading_deg = 3;
}
message TelemetryAck { uint32 points_received = 1; }

message DriverEvent  { /* ... */ }
message DispatchOrder { /* ... */ }

// ---------- Service ----------

service RideService {
  // Unary: one request, one response.
  rpc GetRide(GetRideRequest) returns (Ride);

  // Server streaming: subscribe to a ride's progress.
  rpc WatchRide(WatchRideRequest) returns (stream RideUpdate);

  // Client streaming: push GPS points, get one summary back.
  rpc UploadTelemetry(stream TelemetryPoint) returns (TelemetryAck);

  // Bidirectional: driver app and dispatcher talk continuously.
  rpc DriverChannel(stream DriverEvent) returns (stream DispatchOrder);
}
```

A few things worth noticing as you read it.

The field numbers are the real contract, as mentioned before — and `reserved 3` is how you enforce that after a deletion. Without it, someone adds `int32 rating = 3;` two years later, an old binary sends a string in field 3, and the new one either garbles it or crashes. Reserving both the number and the name means the compiler rejects the mistake instead of production discovering it.

Numbers 1–15 encode their tag in a single byte; 16 and up take two. So if `Ride` had a field written on every message in a hot path, you'd want it below 16 and push rarely-set fields higher.

`RIDE_STATUS_UNSPECIFIED = 0` isn't stylistic pedantry. In proto3, scalar and enum fields don't distinguish "absent" from "default" on the wire — an unset enum *is* zero. If you'd assigned `REQUESTED = 0`, then a client that forgot to set the field would silently look like it requested a ride. Reserving zero for "unset" makes that bug visible. The same asymmetry is why `optional int32 fare_cents` is marked explicitly: that keyword makes the generated code carry a presence bit, so `has_fare_cents()` exists and you can tell a free ride from an unpriced one.

Wrapping even one-argument calls in a request message (`GetRideRequest` rather than `rpc GetRide(string)`) is a convention gRPC essentially forces, and it's the right one anyway — when you later need pagination or a field mask, you add a field rather than breaking every caller.

The versioned package (`rideshare.v1`) and its matching directory path are how you run two incompatible generations of an API side by side during a migration. `v2` is a different package with different generated types, so nothing collides.

---

## Q: Can you show me what the payload of that packet looks like?

Let's encode a concrete `Ride` and look at the actual bytes.

```protobuf
Ride {
  id: "r_8Qx"
  rider: Rider { id: "u_42", display_name: "Ada" }
  pickup: LatLng { latitude: 37.7749, longitude: -122.4194 }
  status: RIDE_STATUS_IN_PROGRESS   // = 3
  fare_cents: 1850
}
```

That serializes to 45 bytes:

```
0000: 0A 05 72 5F 38 51 78 12  0B 0A 04 75 5F 34 32 12   |..r_8Qx....u_42.|
0010: 03 41 64 61 22 12 09 D0  D5 56 EC 2F E3 42 40 11   |.Ada"....V./.B@.|
0020: 50 FC 18 73 D7 9A 5E C0  30 03 70 BA 0E            |P..s..^.0.p..|
```

### Walking through it

Every field is a **tag varint** followed by a payload. The tag packs two things: `(field_number << 3) | wire_type`.

| Wire type | Meaning | Used by |
|---|---|---|
| 0 | varint | int32/64, uint, bool, enum |
| 1 | 64-bit | double, fixed64 |
| 2 | length-delimited | string, bytes, nested messages, packed arrays |
| 5 | 32-bit | float, fixed32 |

**`0A 05 72 5F 38 51 78`** — field 1, `id`

`0x0A` = `0000 1010`. Bottom three bits are `010` = wire type 2 (length-delimited); the rest is `1` = field number 1. Then `0x05` is the length, then five ASCII bytes: `r _ 8 Q x`. Notice the name `id` appears nowhere — that's the schema dependency.

**`12 0B ...`** — field 2, `rider`

`0x12` = field 2, wire type 2. `0x0B` = 11 bytes follow. A nested message is encoded exactly like a string: length prefix, then the child's own serialization, recursively:

```
0A 04 75 5F 34 32      field 1 (id),           len 4, "u_42"
12 03 41 64 61         field 2 (display_name), len 3, "Ada"
```

That structural identity between "string" and "nested message" is why `protoc --decode_raw` can print a rough tree without the `.proto` file but can't tell you whether field 2 is a submessage or just a string that happens to contain those bytes.

**`22 12 ...`** — field 4, `pickup`

`0x22` = field 4, wire type 2, length `0x12` = 18. Inside:

```
09  D0 D5 56 EC 2F E3 42 40    field 1, wire type 1 → double 37.7749
11  50 FC 18 73 D7 9A 5E C0    field 2, wire type 1 → double -122.4194
```

Doubles are raw IEEE-754, little-endian. Read `D0 D5 56 EC 2F E3 42 40` backwards and you get `0x4042E32FEC56D5D0` — sign bit 0, exponent `0x404` (biased, so 2⁵), mantissa the rest. No compression, no text conversion, just the bits your FPU already had.

**`30 03`** — field 6, `status`

`0x30` = `0011 0000` → field 6, wire type 0. Enums are plain varints, so `IN_PROGRESS` costs a single byte. This is where `UNSPECIFIED = 0` pays off in a way you can see: had the field been unset, these two bytes would simply be *absent* from the message, and the parser would hand you zero. "Absent" and "zero" are genuinely the same thing on the wire.

**`70 BA 0E`** — field 14, `fare_cents = 1850`

`0x70` → field 14, wire type 0 — still one tag byte, because 14 < 16. The varint takes seven bits per byte, low group first, with the high bit as a continuation flag:

```
BA = 1011 1010   continue, payload 0111010 = 58
0E = 0000 1110   stop,     payload 0001110 = 14

58 + (14 × 128) = 1850
```

### The comparison

The equivalent JSON runs about 160 bytes:

```json
{"id":"r_8Qx","rider":{"id":"u_42","displayName":"Ada"},"pickup":{"latitude":37.7749,"longitude":-122.4194},"status":"RIDE_STATUS_IN_PROGRESS","fareCents":1850}
```

Roughly 3.5× larger, and the gap widens with numeric data — `-122.4194` is 9 characters of text that a parser has to run through a decimal-to-binary conversion, versus 8 bytes that get memcpy'd. It narrows again for string-heavy payloads, where both formats are mostly carrying the same UTF-8.

### What actually goes on the wire

That 45-byte blob isn't a packet by itself. gRPC wraps each message in a 5-byte frame — one compression flag, then a **big-endian** 4-byte length (note the endianness flip from the doubles inside):

```
00 00 00 00 2D  <45 bytes above>
```

That 50-byte unit becomes the body of an HTTP/2 DATA frame, which has its own 9-byte header:

```
00 00 32   length = 50
00         type = DATA
01         flags = END_STREAM
00 00 00 01  stream identifier
```

Preceded, on a separate HEADERS frame, by the HPACK-compressed pseudo-headers — `:method: POST`, `:path: /rideshare.v1.RideService/GetRide`, `content-type: application/grpc+proto`. The RPC method name is literally a URL path; gRPC is HTTP/2 the whole way down. And all of that typically sits inside TLS, so a packet capture shows you none of it without keys.

If you want to poke at this yourself: `protoc --encode=rideshare.v1.Ride rideshare.proto < msg.txtpb | xxd` will reproduce the dump, and `protoc --decode_raw < blob.bin` will show you what a parser sees when it has the bytes but not the schema.