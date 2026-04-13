import threading
import sys
import os
import socket
import ssl
import queue
import time

dashboard_lock = threading.Lock()

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import *
from utils.logger import log_event
from utils.helpers import parse_message, is_duplicate


buffer = queue.Queue()
clients = {}
events = []
total_packets = 0
start_time = time.time()

#  RATE LIMIT STORAGE
client_requests = {}

#  SSL SETUP
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

print(f"[SECURE SERVER STARTED] {SERVER_IP}:{SERVER_PORT}")


def classify(event):
    if event["type"] == "CPU":
        return "HIGH" if event["value"] > 80 else "NORMAL"
    if event["type"] == "MEMORY":
        return "HIGH" if event["value"] > 70 else "NORMAL"
    return "OK"


def display_dashboard():
    with dashboard_lock:
        print("\033[H\033[J", end="")
        print("===== LIVE SYSTEM MONITOR =====\n")
        print(f"{'Node':<20}{'Type':<10}{'Value':<10}{'Status':<10}")
        print("-" * 60)

        for e in events[-10:]:
            node = f"{e['node_id']}"
            print(f"{node:<20}{e['type']:<10}{e['value']:<10}{classify(e):<10}")

        print("\nClients:", len(clients))


def handle_client(conn, addr):
    global total_packets

    clients[addr] = True
    print(f"[CONNECTED] {addr}")

    while True:
        try:
            data = conn.recv(BUFFER_SIZE)
            if not data:
                break

            current_time = time.time()

            #  RATE LIMIT LOGIC
            if addr not in client_requests:
                client_requests[addr] = []

            client_requests[addr] = [
                t for t in client_requests[addr]
                if current_time - t < RATE_WINDOW
            ]

            if len(client_requests[addr]) >= RATE_LIMIT:
                conn.send("RATE LIMIT EXCEEDED".encode())
                print(f"[RATE LIMIT] {addr} blocked")
                continue

            client_requests[addr].append(current_time)

            messages = data.decode().split("\n")

            for msg in messages:
                if not msg.strip():
                    continue

                msg_type, value = parse_message(msg)

                if msg_type is None:
                    conn.send("INVALID".encode())
                    continue

                event = {
                    "node_id": f"{addr[0]}:{addr[1]}",
                    "type": msg_type,
                    "value": value,
                    "timestamp": time.time()
                }

                if is_duplicate(event):
                    continue

                buffer.put((event, conn))
                total_packets += 1

        except:
            break

    conn.close()
    clients.pop(addr, None)
    client_requests.pop(addr, None)
    print(f"[DISCONNECTED] {addr}")


def process_packets():
    while True:
        event, conn = buffer.get()

        log_event(event)
        events.append(event)

        if len(events) % 2 == 0:
            display_dashboard()

        if event["type"] == "CPU":
            response = "CPU RECEIVED"
        elif event["type"] == "MEMORY":
            response = "MEMORY RECEIVED"
        elif event["type"] == "PING":
            response = "PONG"
        else:
            response = "INVALID"

        try:
            conn.send(response.encode())
        except:
            pass


def metrics():
    while True:
        time.sleep(5)
        elapsed = time.time() - start_time
        print(f"\n[METRICS] {total_packets/elapsed:.2f} packets/sec")


def accept_clients():
    while True:
        client_socket, addr = server_socket.accept()

        try:
            secure_conn = context.wrap_socket(client_socket, server_side=True)
        except ssl.SSLError as e:
            print(f"[SSL ERROR] {addr}: {e}")
            client_socket.close()
            continue

        threading.Thread(
            target=handle_client,
            args=(secure_conn, addr),
            daemon=True
        ).start()


threading.Thread(target=accept_clients, daemon=True).start()

for _ in range(WORKER_THREADS):
    threading.Thread(target=process_packets, daemon=True).start()

threading.Thread(target=metrics, daemon=True).start()

while True:
    time.sleep(1)