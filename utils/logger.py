def log_event(event):
    with open("data/events.log", "a") as f:
        f.write(str(event) + "\n")