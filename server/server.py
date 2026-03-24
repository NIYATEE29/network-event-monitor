import socket
import threading
import queue
import base64
import time

# 🔗 IMPORT PROCESSOR (IMPORTANT LINK)
from processor.processor import EventProcessor

SERVER_IP = "0.0.0.0"
SERVER_PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

buffer = queue.Queue()
clients = set()

# 🔗 CREATE PROCESSOR INSTANCE
processor = EventProcessor()

print(f"[SERVER STARTED] {SERVER_IP}:{SERVER_PORT}")


# 🔐 SIMPLE ENCRYPTION (simulation)
def encrypt(msg):
    return base64.b64encode(msg.encode())

def decrypt(msg):
    return base64.b64decode(msg).decode()


# 📥 RECEIVE THREAD
def receive_packets():
    while True:
        try:
            data, addr = server_socket.recvfrom(1024)

            if addr not in clients:
                clients.add(addr)
                print(f"[NEW CLIENT] {addr}")

            buffer.put((data, addr))

        except Exception as e:
            print(f"[ERROR RECEIVE] {e}")


# 🧠 PROCESS THREAD (NOW CONNECTED TO PROCESSOR)
def process_packets():
    while True:
        data, addr = buffer.get()

        try:
            # 🔓 Step 1: Decrypt
            message = decrypt(data)

            # 🔗 Step 2: SEND TO PROCESSOR
            processed_event = processor.process_event(message)

            # ❗ If duplicate or invalid → skip
            if processed_event is None:
                continue

            # 📊 Step 3: Display processed result
            print(f"\n[PROCESSED EVENT]")
            print(processed_event)

            # 📊 OPTIONAL DASHBOARD
            display_dashboard(processor.events)

            # 🔁 Step 4: Send ACK
            response = encrypt(f"ACK: {processed_event['event_type']}")
            server_socket.sendto(response, addr)

        except Exception as e:
            print(f"[ERROR PROCESS] {e}")


# 📊 DASHBOARD FUNCTION
def display_dashboard(events):
    print("\033[H\033[J")  # clear screen
    print("===== LIVE DASHBOARD =====")

    for e in events[-10:]:
        print(f"{e['node_id']} | {e['event_type']} | {e['severity']} | {e['timestamp']}")


# 🚀 START THREADS
threading.Thread(target=receive_packets, daemon=True).start()

for _ in range(5):
    threading.Thread(target=process_packets, daemon=True).start()


# 🔄 KEEP SERVER RUNNING
while True:
    pass