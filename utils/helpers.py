seen_events = set()

def is_duplicate(event):
    event_id = f"{event['node_id']}_{event['timestamp']}"
    if event_id in seen_events:
        return True
    seen_events.add(event_id)
    return False


def sort_events(events):
    return sorted(events, key=lambda x: x["timestamp"])