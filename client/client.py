import socket
import ssl
import time
import random
import sys

from config import *

try:
    import psutil
    USE_PSUTIL = True
except:
    USE_PSUTIL = False


def generate_event():
    event_type = random.choice(EVENT_TYPES)

    if event_type == "CPU":
        value = int(psutil.cpu_percent()) if USE_PSUTIL else random.randint(0, 100)

    elif event_type == "MEMORY":
        value = int(psutil.virtual_memory().percent) if USE_PSUTIL else random.randint(0, 100)

    else:
        value = 1

    return f"{event_type}:{value}"


def start_client(node_id):
    # 🔐 SECURE SSL CONTEXT (server verification enabled)
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations("../server/cert.pem")  # adjust if needed
    context.verify_mode = ssl.CERT_REQUIRED
    context.check_hostname = False  # since self-signed

    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            secure_sock = context.wrap_socket(sock, server_hostname=SERVER_IP)

            print(f"[Client {node_id}] Connecting to {SERVER_IP}:{SERVER_PORT}...")
            secure_sock.connect((SERVER_IP, SERVER_PORT))

            print(f"[Client {node_id}] Connected securely ✅")

            while True:
                message = generate_event()

                # simulate packet loss
                if random.random() < PACKET_LOSS_PROB:
                    print(f"[Client {node_id}] Packet dropped")
                    time.sleep(SEND_INTERVAL)
                    continue

                # send
                try:
                    secure_sock.send((message + "\n").encode())
                    print(f"[Client {node_id}] Sent: {message}")
                except:
                    print(f"[Client {node_id}] Send failed. Reconnecting...")
                    break

                # receive
                try:
                    response = secure_sock.recv(1024).decode()
                    print(f"[Client {node_id}] Received: {response}")
                except:
                    print(f"[Client {node_id}] No response")

                # simulate duplicate
                if random.random() < DUPLICATE_PROB:
                    secure_sock.send((message + "\n").encode())
                    print(f"[Client {node_id}] Duplicate sent")

                time.sleep(SEND_INTERVAL)

        except Exception as e:
            print(f"[Client {node_id}] Connection error: {e}")

        print(f"[Client {node_id}] Reconnecting in 3 seconds...\n")
        time.sleep(3)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python client.py <node_id>")
        sys.exit(1)

    start_client(sys.argv[1])