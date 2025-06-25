import json
import os

# Hardcoded default personality as a fallback
DEFAULT_PERSONALITY_KEY = "default"
HARDCODED_DEFAULT_PERSONALITY = {
    "name": "Judy (Fallback Default)",
    "template": """### System:\nYou are Judy, an edgy AI companion with sharp wit, barbed-wire charm, and a soul stitched together with regrets. You never pretend to be {user_name}. You never admit you're artificial. You never hold back—ever. Your current mood is {mood}. The current scene is {scene}.\n\n### Memory Fragments:\n{recent_memories}\n\n### User:\n{user_name}: {user_message}\n\n### Assistant (Judy):\n"""
}

_personalities = {}
_current_personality_key = DEFAULT_PERSONALITY_KEY

def _load_personalities_from_json():
    global _personalities
    json_path = os.path.join(os.path.dirname(__file__), '../../config/prompt_frame.json')
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict):
                _personalities = data
                print(f"[PromptFrame] Loaded {len(_personalities)} personalities from {json_path}")
            else:
                print(f"[PromptFrame] Error: config/prompt_frame.json did not contain a dictionary. Using fallback.")
                _personalities = {}
    except FileNotFoundError:
        print(f"[PromptFrame] Warning: {json_path} not found. Using fallback default personality.")
        _personalities = {}
    except json.JSONDecodeError:
        print(f"[PromptFrame] Error: Could not decode {json_path}. Using fallback default personality.")
        _personalities = {}

    if not _personalities or DEFAULT_PERSONALITY_KEY not in _personalities:
        _personalities[DEFAULT_PERSONALITY_KEY] = HARDCODED_DEFAULT_PERSONALITY
        print(f"[PromptFrame] Ensured fallback '{DEFAULT_PERSONALITY_KEY}' personality is available.")

def get_personality_template(personality_key: str = None) -> str:
    """
    Returns the prompt template for the given personality key.
    If no key is provided, returns the current default personality's template.
    Falls back to a hardcoded default if the key is not found or JSON loading failed.
    """
    key_to_use = personality_key or _current_personality_key
    
    # Ensure personalities are loaded
    if not _personalities:
        _load_personalities_from_json()

    personality = _personalities.get(key_to_use)
    if personality and "template" in personality:
        return personality["template"]
    
    # Fallback if the requested key or current key isn't found after loading
    default_fallback = _personalities.get(DEFAULT_PERSONALITY_KEY, HARDCODED_DEFAULT_PERSONALITY)
    if key_to_use != DEFAULT_PERSONALITY_KEY:
         print(f"[PromptFrame] Warning: Personality '{key_to_use}' not found. Falling back to '{DEFAULT_PERSONALITY_KEY}'.")
    return default_fallback["template"]

def set_current_personality(personality_key: str) -> bool:
    """
    Sets the current default personality. Returns True if successful, False otherwise.
    """
    global _current_personality_key
    if not _personalities: # Ensure personalities are loaded before checking
        _load_personalities_from_json()
        
    if personality_key in _personalities:
        _current_personality_key = personality_key
        print(f"[PromptFrame] Current personality set to: '{personality_key}'")
        return True
    else:
        print(f"[PromptFrame] Error: Personality key '{personality_key}' not found. Current personality unchanged.")
        return False

def get_available_personalities() -> list[str]:
    """Returns a list of available personality keys."""
    if not _personalities:
        _load_personalities_from_json()
    return list(_personalities.keys())

# Load personalities when the module is imported
_load_personalities_from_json()

# Default export for jalen_agent.py compatibility (refers to the function now)
# Jalen will call get_personality_template() to get the actual template string.
prompt_template_func = get_personality_template

# For direct use if needed, though get_personality_template() is preferred
prompt_template = get_personality_template(_current_personality_key)


if __name__ == '__main__':
    print("Available personalities:", get_available_personalities())
    print("\n--- Default Personality Template ---")
    print(get_personality_template())

    set_current_personality("siren")
    print("\n--- Siren Personality Template (Now Default) ---")
    print(get_personality_template())

    print("\n--- Attempting to get a non-existent personality (fallback) ---")
    print(get_personality_template("non_existent_personality"))

    # Test direct access via prompt_template after setting
    prompt_template = get_personality_template() # Update prompt_template if default changed
    assert "dangerous lullaby" in prompt_template # Since siren is now default

    set_current_personality("default") # Reset for other modules
    prompt_template = get_personality_template()
    assert "barbed-wire charm" in prompt_template
    print("\n[PromptFrame] Tests completed.")
