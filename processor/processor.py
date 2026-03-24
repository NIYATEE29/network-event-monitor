import json
from processor.classifier import EventClassifier
from utils.helpers import is_duplicate, sort_events
from utils.logger import log_event

class EventProcessor:

    def __init__(self):
        self.classifier = EventClassifier()
        self.events = []

    def process_event(self, raw_data):
        try:
            event = json.loads(raw_data)

            # 1. Remove duplicates
            if is_duplicate(event):
                return None

            # 2. Classify
            event = self.classifier.classify(event)

            # 3. Store
            self.events.append(event)

            # 4. Sort
            self.events = sort_events(self.events)

            # 5. Log
            log_event(event)

            return event

        except Exception as e:
            print("Processing error:", e)
            return None
    def display_dashboard(events):
        print("\033[H\033[J")  # clear screen

        print("===== LIVE DASHBOARD =====")
        for e in events[-10:]:
            print(f"{e['node_id']} | {e['event_type']} | {e['severity']} | {e['timestamp']}")