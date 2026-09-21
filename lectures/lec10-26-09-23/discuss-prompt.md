# Model Context Protocol (MCP): Overview and Example Messages

## What MCP is

The **Model Context Protocol (MCP)** is an open standard for connecting AI applications to external tools and data. Anthropic introduced it in late 2024, and it has since moved to open governance under the Linux Foundation's Agentic AI Foundation.

MCP standardizes how an LLM application (the **host**, such as Claude or an IDE) talks to external capability providers (**servers**). The host runs one **client** per server connection. The goal is to replace N×M custom integrations with one protocol, much as the Language Server Protocol (LSP) did for editors and language tooling.

### Server primitives

- **Tools:** functions the model can call, such as querying a database or sending a message
- **Resources:** readable data, such as files or records, identified by URIs
- **Prompts:** reusable prompt templates

### Client primitives (offered back to servers)

- **Sampling:** the server asks the host's model to generate text
- **Roots:** filesystem boundaries the server may operate within
- **Elicitation:** the server asks the user for additional input

## Protocol stack

### Message layer: JSON-RPC 2.0

All communication consists of JSON-RPC 2.0 requests, responses, and notifications. A session begins with an `initialize` handshake that negotiates the protocol version and capabilities. The connection is stateful and bidirectional, so either side can send requests.

### Transports

| Transport | Use case | Mechanism |
|---|---|---|
| **stdio** | Local servers | The client launches the server as a subprocess and exchanges newline-delimited JSON-RPC over stdin/stdout. No network is involved. |
| **Streamable HTTP** | Remote servers | The client POSTs JSON-RPC messages to a single endpoint. The server responds with plain JSON or upgrades the response to a **Server-Sent Events (SSE)** stream for streaming results and server-initiated messages. Sessions are tracked with an `Mcp-Session-Id` header, and resumability is supported. |
| **Custom** | Anything else | Allowed as long as it carries JSON-RPC. WebSocket is a common community option. |

Streamable HTTP replaced the original HTTP+SSE transport, which used two separate endpoints, in the March 2025 spec revision.

### Security

- HTTP transports run over **TLS**.
- Authorization is based on **OAuth 2.1**: the MCP server acts as a resource server, with protected-resource metadata and dynamic client registration.

## Example session

This example shows a session between a host (client) and a server that exposes one tool, a simple latency probe. Over stdio each message would be a single line of JSON. Over Streamable HTTP each would be a POST body. The messages are pretty-printed here for readability.

### 1. Client → Server: `initialize` request

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "roots": { "listChanged": true },
      "sampling": {}
    },
    "clientInfo": { "name": "ExampleHost", "version": "1.0.0" }
  }
}
```

### 2. Server → Client: `initialize` response

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18",
    "capabilities": {
      "tools": { "listChanged": true }
    },
    "serverInfo": { "name": "net-probe", "version": "0.2.0" }
  }
}
```

### 3. Client → Server: `initialized` notification

A notification has no `id`, so no response is expected.

```json
{ "jsonrpc": "2.0", "method": "notifications/initialized" }
```

### 4. Client → Server: discover tools

```json
{ "jsonrpc": "2.0", "id": 2, "method": "tools/list" }
```

### 5. Server → Client: tool list

The `inputSchema` is JSON Schema, and the model uses it to form arguments.

```json
{
  "jsonrpc": "2.0",
  "id": 2,
  "result": {
    "tools": [
      {
        "name": "ping_host",
        "description": "Measure round-trip latency to a host",
        "inputSchema": {
          "type": "object",
          "properties": {
            "host":  { "type": "string" },
            "count": { "type": "integer", "default": 4 }
          },
          "required": ["host"]
        }
      }
    ]
  }
}
```

### 6. Client → Server: call the tool

The host sends this after the model decides to use the tool.

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "method": "tools/call",
  "params": {
    "name": "ping_host",
    "arguments": { "host": "example.com", "count": 3 }
  }
}
```

### 7. Server → Client: tool result

```json
{
  "jsonrpc": "2.0",
  "id": 3,
  "result": {
    "content": [
      { "type": "text", "text": "3 packets, 0% loss, RTT min/avg/max = 11.2/12.8/15.1 ms" }
    ],
    "isError": false
  }
}
```

The host feeds the returned `content` back into the model's context. If the server's tool set changes later, the server can push a `notifications/tools/list_changed` notification, and the client re-runs `tools/list`.

## The same `tools/call` over Streamable HTTP

```http
POST /mcp HTTP/1.1
Host: probe.example.net
Content-Type: application/json
Accept: application/json, text/event-stream
Mcp-Session-Id: 7f3c9a2e-...
MCP-Protocol-Version: 2025-06-18
Authorization: Bearer <token>

{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"ping_host","arguments":{"host":"example.com","count":3}}}
```

The server can reply in either of two ways:

- `Content-Type: application/json`, with the JSON-RPC result directly in the body
- `Content-Type: text/event-stream`, sending progress notifications as SSE events followed by the final result

## Notes

- The `protocolVersion` string depends on which spec revision the client and server both support. `2025-06-18` is used here only as an example.
- The spec is revised periodically. For protocol-level details such as auth flows or session semantics, see the current specification at <https://modelcontextprotocol.io>.

## Bonus Prompt

What is MPC?

### Response

"MPC" has a few common meanings, and the protocol answer depends on which one you mean. Here are the two most likely.

**Model Predictive Control (in adaptive video streaming)**

MPC is a control-theoretic approach to adaptive bitrate (ABR) selection, best known from Yin et al.'s SIGCOMM 2015 paper. The client predicts throughput over a short future horizon (say, the next 5 chunks) and chooses the bitrate sequence that maximizes a QoE objective. That objective typically combines bitrate utility, a rebuffering penalty, and a smoothness penalty for bitrate switches. The client applies only the first decision, then re-plans at the next chunk (receding horizon). RobustMPC improves on this by discounting the throughput estimate by recent prediction error. FastMPC precomputes decisions into a lookup table so they can run cheaply on the client.

MPC is a decision algorithm, not a protocol, so it runs over the normal streaming stack:

- **Application layer:** DASH or HLS. Segments are fetched as ordinary HTTP GETs using an MPD or playlist manifest listing the available bitrate representations.
- **Transport:** HTTP/1.1 or HTTP/2 over TCP, or HTTP/3 over QUIC. MPC's throughput predictor observes whatever the transport's congestion control delivers (CUBIC, BBR, and so on).
- **Measurement inputs:** per-chunk download time and size, plus buffer occupancy. There are no special network signals. That is partly why pairing ABR with lower-latency signals such as L4S/ECN is an active research question.

**Secure Multi-Party Computation (cryptography)**

Here, MPC means several parties jointly compute a function over private inputs without revealing those inputs to each other. The cryptographic protocols involved include:

- Garbled circuits (Yao) with oblivious transfer
- Secret sharing schemes (Shamir, additive), as used in GMW, BGW, and SPDZ

On the network side, it typically uses authenticated point-to-point channels, usually TLS over TCP, and sometimes a broadcast channel. Performance is often dominated by communication rounds and bandwidth, so latency between parties matters a great deal.

If you meant something else, such as Multipath TCP (usually "MPTCP") or the Model Context Protocol ("MCP") for AI tools, let me know and I'll cover that instead.
