import socket
import threading
import queue
import base64
import time

SERVER_IP = "0.0.0.0"
SERVER_PORT = 9999

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((SERVER_IP, SERVER_PORT))

buffer = queue.Queue()
clients = set()

print(f"[SERVER STARTED] {SERVER_IP}:{SERVER_PORT}")


def encrypt(msg):
    return base64.b64encode(msg.encode())

def decrypt(msg):
    return base64.b64decode(msg).decode()


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


def process_packets():
    while True:
        data, addr = buffer.get()

        try:
            message = decrypt(data)
            print(f"[{time.strftime('%H:%M:%S')}] {addr}: {message}")

            response = encrypt(f"ACK: {message}")
            server_socket.sendto(response, addr)

        except Exception as e:
            print(f"[ERROR PROCESS] {e}")


threading.Thread(target=receive_packets, daemon=True).start()

for _ in range(5):
    threading.Thread(target=process_packets, daemon=True).start()

while True:
    pass