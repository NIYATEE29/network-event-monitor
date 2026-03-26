import os

def log_event(event):
    os.makedirs("data", exist_ok=True)

    with open("data/events.log", "a") as f:
        f.write(str(event) + "\n")