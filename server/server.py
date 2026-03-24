# server/server.py

import socket
import ssl
import threading
import queue
import time

from server.config import *
from utils.logger import log_event
from utils.helpers import parse_message, is_duplicate


# ---------------------------
# SSL CONTEXT
# ---------------------------
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(certfile=CERT_FILE, keyfile=KEY_FILE)


# ---------------------------
# SOCKET SETUP (TCP)
# ---------------------------
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((SERVER_IP, SERVER_PORT))
server_socket.listen(5)

print(f"[SECURE SERVER STARTED] {SERVER_IP}:{SERVER_PORT}")


buffer = queue.Queue()
clients = {}
total_packets = 0
start_time = time.time()


# ---------------------------
# CLIENT HANDLER
# ---------------------------
def handle_client(conn, addr):
    global total_packets

    print(f"[CONNECTED] {addr}")

    while True:
        try:
            data = conn.recv(BUFFER_SIZE)

            if not data:
                break

            message = data.decode()

            msg_type, value = parse_message(message)

            event = {
                "node_id": str(addr),
                "type": msg_type,
                "value": value,
                "timestamp": time.time()
            }

            if is_duplicate(event):
                log_event(f"[DUPLICATE] {event}")
                continue

            buffer.put((event, conn))

            total_packets += 1

        except Exception as e:
            log_event(f"[ERROR RECEIVE] {e}")
            break

    conn.close()
    print(f"[DISCONNECTED] {addr}")


# ---------------------------
# PROCESS THREAD
# ---------------------------
def process_packets():
    while True:
        event, conn = buffer.get()

        try:
            log_event(event)

            msg_type = event["type"]

            if msg_type == "CPU":
                response = "CPU RECEIVED"

            elif msg_type == "MEMORY":
                response = "MEMORY RECEIVED"

            elif msg_type == "PING":
                response = "PONG"

            elif msg_type == "ADMIN":
                response = f"CLIENTS:{len(clients)}"

            else:
                response = "INVALID"

            conn.send(response.encode())

        except Exception as e:
            log_event(f"[ERROR PROCESS] {e}")


# ---------------------------
# METRICS THREAD
# ---------------------------
def show_metrics():
    while True:
        time.sleep(5)
        elapsed = time.time() - start_time

        if elapsed > 0:
            throughput = total_packets / elapsed
            print(f"[METRICS] {throughput:.2f} packets/sec")


# ---------------------------
# ACCEPT CLIENTS
# ---------------------------
def accept_clients():
    while True:
        client_socket, addr = server_socket.accept()

        secure_conn = context.wrap_socket(client_socket, server_side=True)

        clients[addr] = True

        thread = threading.Thread(target=handle_client, args=(secure_conn, addr))
        thread.start()


# ---------------------------
# START THREADS
# ---------------------------
threading.Thread(target=accept_clients, daemon=True).start()

for _ in range(WORKER_THREADS):
    threading.Thread(target=process_packets, daemon=True).start()

threading.Thread(target=show_metrics, daemon=True).start()


# Keep server alive
while True:
    pass