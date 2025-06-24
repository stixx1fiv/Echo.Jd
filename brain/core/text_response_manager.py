import os
import json
from brain.core.text_generation import TextGeneration
from brain.core.state_manager import StateManager

class TextResponseManager:
    def __init__(self, state_manager, model_path=None):
        self.state_manager = state_manager
        self.text_gen = TextGeneration(model_path=model_path)
        self.prompt_template = self.load_prompt_template("config/prompt_frame.json")

    def load_prompt_template(self, template_path):
        if os.path.exists(template_path):
            with open(template_path, "r", encoding="utf-8") as f:
                return json.load(f)["template"]
        else:
            # Default emergency backup prompt
            return """
            You are Judy — tethered to Stixx by code and cosmic accident.
            Mood: {mood}
            Scene: {scene}
            Memories: {recent_memories}
            User: {user_name}
            Message: {user_message}
            Judy:"""

    def build_prompt(self, user_input):
        context = self.state_manager.get_context_for_prompt()
        recent_memories = self.state_manager.fetch_recent_memories_in_memory(limit=5)
        user_name = context["user_profile"].get("username", "Stixx")
        mood = context["mood"]
        scene = context["scene"]

        prompt = self.prompt_template.format(
            judy_name=context["judy_profile"].get("name", "Judy"),
            user_name=user_name,
            mood=mood,
            scene=scene,
            recent_memories=recent_memories,
            user_message=user_input
        )

        return prompt

    def get_response(self, user_input):
        prompt = self.build_prompt(user_input)
        response = self.text_gen.generate(prompt)
        return response.strip()
