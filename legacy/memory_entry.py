from datetime import datetime
from uuid import uuid4

class MemoryEntry:
    def __init__(self, content, importance=0.5, mood_tag="neutral", types=None,
                 topic_tags=None, ambient_tags=None, decay_rate=0.01):
        self.uuid = str(uuid4())
        self.content = content
        self.importance = importance  # 0.0 to 1.0
        self.mood_tag = mood_tag
        self.types = types or []
        self.topic_tags = topic_tags or []
        self.ambient_tags = ambient_tags or []
        self.decay_rate = decay_rate  # Decay factor per day
        self.timestamp = datetime.utcnow().isoformat()
        self.adjacent_uuids = []

    def to_dict(self):
        return self.__dict__

    @staticmethod
    def from_dict(data):
        entry = MemoryEntry(
            content=data["content"],
            importance=data.get("importance", 0.5),
            mood_tag=data.get("mood_tag", "neutral"),
            types=data.get("types", []),
            topic_tags=data.get("topic_tags", []),
            ambient_tags=data.get("ambient_tags", []),
            decay_rate=data.get("decay_rate", 0.01)
        )
        entry.uuid = data.get("uuid", str(uuid4()))
        entry.timestamp = data.get("timestamp", datetime.utcnow().isoformat())
        entry.adjacent_uuids = data.get("adjacent_uuids", [])
        return entry
