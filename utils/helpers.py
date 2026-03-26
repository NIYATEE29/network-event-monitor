seen_events = set()

def is_duplicate(event):
    key = f"{event['node_id']}_{event['timestamp']}"
    if key in seen_events:
        return True
    seen_events.add(key)
    return False


def parse_message(message):
    try:
        if ":" not in message:
            return None, None

        msg_type, value = message.split(":", 1)

        msg_type = msg_type.strip().upper()
        value = int(float(value.strip()))

        return msg_type, value

    except:
        return None, None