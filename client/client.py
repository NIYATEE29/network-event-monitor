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
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    context = ssl._create_unverified_context()
    secure_sock = context.wrap_socket(sock, server_hostname=SERVER_IP)

    secure_sock.connect((SERVER_IP, SERVER_PORT))
    print(f"Client {node_id} connected securely")

    try:
        while True:
            message = generate_event()

            if random.random() < PACKET_LOSS_PROB:
                print(f"[Client {node_id}] Packet dropped")
                time.sleep(SEND_INTERVAL)
                continue

            try:
                secure_sock.send((message + "\n").encode())
            except:
                print("Connection lost")
                break

            print(f"[Client {node_id}] Sent: {message}")

            try:
                response = secure_sock.recv(1024).decode()
                print(f"[Client {node_id}] Received: {response}")
            except:
                print(f"[Client {node_id}] No response")

            if random.random() < DUPLICATE_PROB:
                secure_sock.send((message + "\n").encode())
                print(f"[Client {node_id}] Duplicate sent")

            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        secure_sock.close()


if __name__ == "__main__":
    start_client(sys.argv[1])