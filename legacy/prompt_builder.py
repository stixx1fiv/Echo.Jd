from judy_prompts import personalities, prompt_template_default

def build_prompt(user_input, mood, scene, memories, personality="default", user_name="Stixx", judy_name="Judy"):
    """
    Build a custom Judy prompt from user input, mood, scene, memories, and selected personality.
    """
    template = personalities.get(personality, prompt_template_default)
    recent_memories = "; ".join(memories) if memories else "None"

    prompt = template.format(
        judy_name=judy_name,
        user_name=user_name,
        mood=mood,
        scene=scene,
        recent_memories=recent_memories,
        user_message=user_input
    )
    return prompt
