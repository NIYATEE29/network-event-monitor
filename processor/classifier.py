class EventClassifier:

    def classify(self, event):
        if event["event_type"] == "CPU_HIGH":
            event["severity"] = "HIGH"

        elif event["event_type"] == "MEMORY_HIGH":
            event["severity"] = "MEDIUM"

        elif event["event_type"] == "DISK_FAIL":
            event["severity"] = "CRITICAL"

        else:
            event["severity"] = "LOW"

        return event