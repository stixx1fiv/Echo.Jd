from datetime import datetime

def score_memory(memory, current_mood, query_tags, mood_map):
    importance_weight = memory.importance * 0.5

    mood_match = 1 if memory.mood_tag == current_mood else (
        0.75 if current_mood in mood_map.get(memory.mood_tag, []) else 0.5
    )
    mood_weight = mood_match * 0.3

    topic_matches = len(set(memory.topic_tags) & set(query_tags))
    topic_weight = topic_matches * 0.1

    ambient_matches = len(set(memory.ambient_tags) & set(query_tags))
    ambient_weight = ambient_matches * 0.05

    days_passed = (datetime.utcnow() - datetime.fromisoformat(memory.timestamp)).days
    decay_penalty = memory.decay_rate * days_passed

    total_score = (importance_weight + mood_weight + topic_weight + ambient_weight) - decay_penalty
    return total_score
