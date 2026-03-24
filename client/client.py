# client/client.py

import socket
import time
import random
import json
import sys

from config import (
    SERVER_IP,
    SERVER_PORT,
    SEND_INTERVAL,
    PACKET_LOSS_PROB,
    DUPLICATE_PROB,
    EVENT_TYPES
)

# Attempt to use real system metrics if available
try:
    import psutil
    USE_PSUTIL = True
except ImportError:
    USE_PSUTIL = False


def generate_event(node_id):
    """
    Generates a system event (CPU, MEMORY, or FAILURE)
    """

    event_type = random.choice(EVENT_TYPES)

    if event_type == "CPU":
        if USE_PSUTIL:
            value = psutil.cpu_percent(interval=1)
        else:
            value = random.randint(0, 100)

    elif event_type == "MEMORY":
        if USE_PSUTIL:
            value = psutil.virtual_memory().percent
        else:
            value = random.randint(0, 100)

    else:
        value = random.choice(["CRASH", "RECOVERED"])

    event = {
        "node_id": node_id,
        "event_type": event_type,
        "value": value,
        "timestamp": time.time()
    }

    return json.dumps(event)


def send_event(sock, message):
    """
    Sends an event while simulating packet loss and duplication
    """

    # Simulate packet loss
    if random.random() < PACKET_LOSS_PROB:
        print("Packet dropped")
        return

    # Send message
    sock.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
    print("Sent:", message)

    # Simulate duplicate message
    if random.random() < DUPLICATE_PROB:
        sock.sendto(message.encode(), (SERVER_IP, SERVER_PORT))
        print("Duplicate message sent")


def start_client(node_id):
    """
    Initializes and runs the UDP client
    """

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    print("Client", node_id, "started")
    print("Sending data to", SERVER_IP, "on port", SERVER_PORT)

    try:
        while True:
            event = generate_event(node_id)
            send_event(sock, event)
            time.sleep(SEND_INTERVAL)

    except KeyboardInterrupt:
        print("Client stopped")
        sock.close()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python client.py <node_id>")
        sys.exit(1)

    node_id = sys.argv[1]
    start_client(node_id)