# client/config.py

# Server configuration
SERVER_IP = "127.0.0.1"
SERVER_PORT = 9999

# Client behavior
SEND_INTERVAL = 2  # seconds between events

# Network simulation parameters
PACKET_LOSS_PROB = 0.2   # probability of dropping a packet
DUPLICATE_PROB = 0.1     # probability of sending duplicate packet

# Event types
EVENT_TYPES = ["CPU", "MEMORY", "FAILURE"]