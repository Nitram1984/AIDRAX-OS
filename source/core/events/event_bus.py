class EventBus:
    def __init__(self):
        self.events = []

    def publish(self, topic, payload=None):
        event = {
            "topic": topic,
            "payload": payload or {}
        }
        self.events.append(event)
        return event

    def list_events(self):
        return self.events

    def health(self):
        return {
            "status": "GREEN",
            "event_count": len(self.events)
        }
