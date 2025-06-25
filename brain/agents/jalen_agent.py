import threading
import time
import datetime
import json
import os
import concurrent.futures
from brain.core.text_generation import TextGeneration

# Attempt to import the rich Judy prompt template. If that fails (e.g., because
# the module is not on the Python path when this file is executed as a script),
# fall back to a minimal template that still provides the required placeholders
# so that `.format(...)` calls succeed.
try:
    # Import the function to get templates and the function to set the current personality
    from brain.core.prompt_frame import get_personality_template, set_current_personality, get_available_personalities # type: ignore
except ImportError:
    # Fallback if the import fails (e.g. module not found)
    def get_personality_template(key=None): # Add key=None for compatibility
        print("[JalenAgent] CRITICAL: brain.core.prompt_frame not found. Using minimal fallback template.")
        return """{judy_name} (mood: {mood}, scene: {scene})\nRecent memories:\n{recent_memories}\n{user_name} said: {user_message}\n{judy_name}:"""
    def set_current_personality(key):
        print("[JalenAgent] CRITICAL: brain.core.prompt_frame not found. Cannot switch personality.")
        return False
    def get_available_personalities():
        return ["default (fallback)"]

class JalenAgent:
    def __init__(self, memory_daemon, state_manager, model_path=None, n_gpu_layers=None, log_prompts=False):
        self.state_manager = state_manager
        self.memory_daemon = memory_daemon
        self._running = False
        self._input_thread = None
        # Forward both parameters so `TextGeneration` can decide what to do with them.
        self.text_gen = TextGeneration(model_path=model_path, n_gpu_layers=n_gpu_layers, log_prompts=True)

    def start_chatbox(self):
        if self._running:
            print("[Judy🌹] Chatbox already running.")
            return
        print("[Judy🌹] Starting CLI chatbox...")
        self._running = True
        self._input_thread = threading.Thread(target=self._chat_loop, daemon=True)
        self._input_thread.start()

    def _chat_loop(self):
        while self._running:
            try:
                message = input("📨 You: ")
                if message.lower() in ["exit", "quit"]:
                    print("[Judy🌹] Shutting down chatbox.")
                    self._running = False
                    break

                # Store user input in both legacy and ChromaDB memory
                self.memory_daemon.add_memory({"timestamp": datetime.datetime.now().isoformat(), "text": f"User: {message}"}, memory_type="short")
                self.state_manager.add_memory_chroma(f"User: {message}", memory_type="short", metadata={"timestamp": time.time(), "role": "user"})

                # Run Judy's response in a background thread and print when ready
                def print_response(response):
                    # Store Judy's response in both legacy and ChromaDB memory
                    self.memory_daemon.add_memory({"timestamp": datetime.datetime.now().isoformat(), "text": f"Judy: {response}"}, memory_type="short")
                    self.state_manager.add_memory_chroma(f"Judy: {response}", memory_type="short", metadata={"timestamp": time.time(), "role": "judy"})
                    print(f"Judy🌹: {response}")

                self.generate_response_async(message, print_response)
                # Wait for the response to print before accepting new input
                while hasattr(self, '_executor') and any(f.running() for f in getattr(self._executor, '_threads', [])):
                    time.sleep(0.1)

            except Exception as e:
                print(f"[Judy🌹] Error in chat loop: {e}")

    def stop(self):
        print("[Judy🌹] Stopping agent.")
        self._running = False
        if self._input_thread:
            self._input_thread.join()

    def handle_command(self, message):
        """
        Handle special commands, e.g. /switchmodel <model_path>
        """
        if message.startswith("/switchmodel"):
            parts = message.split(maxsplit=1)
            if len(parts) == 2:
                new_model_path = parts[1].strip()
                self.text_gen.switch_model(new_model_path)
                print(f"[JalenAgent] Switched model to: {new_model_path}")
                return f"Judy🌹: Model switched to: {os.path.basename(new_model_path)}"
            else:
                return "Judy🌹: Usage: /switchmodel <path_to_model.gguf>"
        elif message.startswith("/personality"):
            parts = message.split(maxsplit=1)
            if len(parts) == 2:
                new_personality_key = parts[1].strip()
                if set_current_personality(new_personality_key):
                    return f"Judy🌹: Personality switched to '{new_personality_key}'."
                else:
                    available = ", ".join(get_available_personalities())
                    return f"Judy🌹: Unknown personality '{new_personality_key}'. Available: {available}"
            else:
                available = ", ".join(get_available_personalities())
                return f"Judy🌹: Usage: /personality <name>. Available: {available}"
        return None

    def generate_response(self, user_input):
        """
        Generate a response to user_input using the full Judy prompt and core profile.
        """
        # Check for command
        if user_input.startswith("/"):
            cmd_result = self.handle_command(user_input)
            if cmd_result:
                return cmd_result

        # Load Judy's core profile
        core_profile_path = os.path.join(os.path.dirname(__file__), '../core/core_profile.json')
        try:
            with open(core_profile_path, 'r', encoding='utf-8') as f:
                core_profile = json.load(f)
        except Exception:
            core_profile = {}
        # Gather context
        mood = self.state_manager.get_mood() if hasattr(self.state_manager, 'get_mood') else "neutral"
        scene = self.state_manager.state.get("scene", "default")

        # --- Enhanced Memory Retrieval ---
        # 1. Get semantically relevant memories from ChromaDB
        chroma_memories_list = []
        if hasattr(self.state_manager, 'query_chroma_memories'):
            try:
                # Query based on current user input. Could be expanded to include more context.
                chroma_memories_list = self.state_manager.query_chroma_memories(user_input, n_results=3)
            except Exception as e:
                print(f"[JalenAgent] Error querying ChromaDB memories: {e}")
        
        chroma_memories_str = ""
        if chroma_memories_list:
            chroma_memories_str = "Relevant thoughts from the archive:\n" + "\n".join(f"- {mem}" for mem in chroma_memories_list)

        # 2. Get recent conversational memories (existing behavior)
        legacy_recent_memories_str = ""
        if hasattr(self.state_manager, 'get_memories'):
            legacy_memories = self.state_manager.get_memories(memory_type="short") # Raw dicts
            # We want the text, and ensure it's not duplicative of what Chroma might return if Chroma stores full "User: ..." strings
            legacy_recent_memories_list = [m['text'] for m in legacy_memories[-5:] if 'text' in m]
            if legacy_recent_memories_list:
                legacy_recent_memories_str = "Recent conversation snippets:\n" + "\n".join(f"- {mem}" for mem in legacy_recent_memories_list)

        # Combine memory strings
        all_recent_memories = ""
        if chroma_memories_str:
            all_recent_memories += chroma_memories_str
        if legacy_recent_memories_str:
            if all_recent_memories: # if chroma_memories_str was added
                all_recent_memories += "\n\n" # Add some separation
            all_recent_memories += legacy_recent_memories_str
        
        if not all_recent_memories:
            all_recent_memories = "No specific memories recalled for this interaction."
        # --- End of Enhanced Memory Retrieval ---

        # Get current personality template
        current_prompt_template = get_personality_template() # Gets the currently set one

        # Compose prompt
        prompt = current_prompt_template.format(
            judy_name=core_profile.get("name", "Judy"), # Consider making judy_name part of personality
            user_name=core_profile.get("preferred_pet_names", ["Stixx"])[0], # User name can be global
            mood=mood,
            scene=scene,
            recent_memories=recent_memories,
            user_message=user_input
        )
        response = self.text_gen.generate(prompt)
        return response.strip()

    def greet(self):
        """
        Generate Judy's initial greeting for first message in chat or GUI.
        """
        greeting = "Hello! I'm Judy, your AI assistant. How can I help you today?"
        return greeting

    def generate_response_async(self, user_input, callback):
        """
        Run generate_response in a background thread and call callback(result) when done.
        """
        if not hasattr(self, '_executor'):
            self._executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        future = self._executor.submit(self.generate_response, user_input)
        future.add_done_callback(lambda f: callback(f.result()))
