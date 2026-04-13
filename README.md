#  Network Event Monitor

A secure, multithreaded distributed network monitoring system built in Python. Multiple client nodes send real-time system metrics (CPU, memory, ping) to a central server over an encrypted SSL/TLS connection. The server processes, deduplicates, rate-limits, and displays all incoming events on a live terminal dashboard.

---

##  Project Structure

```
network-event-monitor/
├── server/
│   ├── server.py        # Main server — accepts clients, processes events, displays dashboard
│   ├── config.py        # Server config (port, rate limit, buffer size, SSL paths)
│   ├── cert.pem         # SSL certificate (self-signed)
│   └── key.pem          # SSL private key
├── client/
│   ├── client.py        # Client — generates and sends system events over SSL
│   └── config.py        # Client config (server IP, send interval, loss/duplicate probabilities)
├── processor/
│   ├── processor.py     # Standalone event processor (dedup, classify, sort, log)
│   └── classifier.py    # Classifies events by severity (LOW / MEDIUM / HIGH / CRITICAL)
└── utils/
    ├── helpers.py        # parse_message(), is_duplicate(), sort_events()
    └── logger.py         # Appends events to data/events.log
```

---

##  How It Works

1. **Server starts** — binds to port `9999`, loads SSL cert/key, spawns worker threads
2. **Client connects** — performs TLS handshake, verifies server certificate
3. **Client sends events** every 2 seconds — randomly picks CPU, MEMORY, or PING
4. **Server receives** — applies rate limiting, parses, deduplicates
5. **Worker threads** pull from a buffer queue — log, classify, and respond
6. **Live dashboard** refreshes every 2 events showing the last 10 readings

---

##  Security

- **SSL/TLS encryption** on all traffic using a self-signed RSA-2048 / SHA-256 certificate
- Client uses `ssl.CERT_REQUIRED` — connection is refused if certificate doesn't match
- No plaintext data ever transmitted over the socket

---

## Features

| Feature | Description |
|---|---|
| **Multithreading** | Each client gets its own thread; 5 worker threads process the buffer |
| **Rate Limiting** | Max N requests per client per time window (configurable) |
| **Duplicate Detection** | Events keyed by `node_id + timestamp`; duplicates silently dropped |
| **Packet Loss Simulation** | Configurable drop probability to simulate unreliable networks |
| **Live Dashboard** | Terminal dashboard showing last 10 events with severity classification |
| **Metrics Thread** | Prints packets/sec throughput every 5 seconds |

---

## Getting Started

### Prerequisites

```bash
pip install psutil  # optional — falls back to random values if not installed
```

### Run the Server

```bash
cd server
python server.py
```

### Run a Client

```bash
cd client
python client.py NodeA
```

Run multiple clients in separate terminals with different node IDs (`NodeB`, `NodeC`, etc.) to simulate a distributed system.

---

## 🧪 Demo Scenarios

All demos work by editing config files only — no code changes needed.

### 1. Normal Operation (default)
```python
# client/config.py
PACKET_LOSS_PROB = 0.2
DUPLICATE_PROB = 0.1
SEND_INTERVAL = 2
```

### 2. Packet Loss Demo
```python
# client/config.py
PACKET_LOSS_PROB = 0.6   # 60% of packets dropped
DUPLICATE_PROB = 0.0
SEND_INTERVAL = 2
```
Watch the dashboard update far less frequently.

### 3. Duplicate Packet Demo
```python
# client/config.py
PACKET_LOSS_PROB = 0.0
DUPLICATE_PROB = 0.7     # 70% chance of re-sending same event
SEND_INTERVAL = 2
```
Client logs show "Duplicate sent" but the server dashboard ignores them — dedup working.

### 4. Rate Limit Demo
```python
# server/config.py
RATE_LIMIT = 2
RATE_WINDOW = 10

# client/config.py
SEND_INTERVAL = 1        # sends faster than the limit allows
PACKET_LOSS_PROB = 0.0
DUPLICATE_PROB = 0.0
```
Server will print `[RATE LIMIT] addr blocked` and respond with `RATE LIMIT EXCEEDED`.

---

## 📊 Event Classification

| Event Type | Threshold | Status |
|---|---|---|
| CPU | > 80% | HIGH |
| CPU | ≤ 80% | NORMAL |
| MEMORY | > 70% | HIGH |
| MEMORY | ≤ 70% | NORMAL |
| PING | — | OK |

---

## 🔧 Configuration Reference

### `server/config.py`
| Variable | Default | Description |
|---|---|---|
| `SERVER_IP` | `0.0.0.0` | Listen on all interfaces |
| `SERVER_PORT` | `9999` | Port to bind |
| `RATE_LIMIT` | `5` | Max requests per window |
| `RATE_WINDOW` | `10` | Window size in seconds |
| `BUFFER_SIZE` | `2048` | Socket receive buffer |
| `WORKER_THREADS` | `5` | Number of processing threads |

### `client/config.py`
| Variable | Default | Description |
|---|---|---|
| `SERVER_IP` | *(your server IP)* | Server to connect to |
| `SERVER_PORT` | `9999` | Server port |
| `SEND_INTERVAL` | `2` | Seconds between sends |
| `PACKET_LOSS_PROB` | `0.2` | Probability of dropping a packet |
| `DUPLICATE_PROB` | `0.1` | Probability of sending a duplicate |

---

## Concepts Demonstrated

- TCP socket programming with SSL/TLS wrapping
- Multithreading with `threading.Thread` and thread-safe `queue.Queue`
- Producer-consumer pattern (client → buffer → worker threads)
- Rate limiting using sliding time windows
- Duplicate detection using hash sets
- Real-time terminal UI with ANSI escape codes

---

## Notes

- The SSL certificate is **self-signed** — suitable for local/lab use. For production, replace with a CA-signed certificate (e.g., Let's Encrypt).
- `psutil` is optional. If not installed, CPU and memory values are randomly generated.
- Log output is written to `data/events.log` (auto-created on first run).

### 👩‍💻 Contributors
- [Niyatee Singh](https://github.com/NIYATEE29)
- [Nehaa Joshi](https://github.com/NehaaJ05)
- [Nikita Mankani](https://github.com/nikitamankani)

