import os
import sys

# This line attempts to add the project's root directory (one level up from 'brain')
# to the Python path. This can help ensure that imports like 'from brain.core...'
# work correctly when this script might be run in different contexts, although
# for typical FastAPI execution via uvicorn from the project root, this might be redundant.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from brain.core.state_manager import StateManager # Import necessary for type hinting and interaction

class LumenCore:
    """
    Manages and calculates the visual state (colors, effects) for Judy's presence.
    This state is primarily based on Judy's current mood (obtained from StateManager)
    and can also be influenced by specific triggered events (e.g., errors, new messages).
    The visual state is intended to be consumed by a GUI or other rendering component
    to dynamically alter the application's appearance.
    """
    def __init__(self, state_manager: StateManager):
        """
        Initializes the LumenCore.

        Args:
            state_manager: An instance of StateManager, used to fetch the current
                           mood and potentially other system states that might influence visuals.
        """
        self.state_manager = state_manager

        # Defines base visual properties (colors) associated with different moods.
        # Keys are mood strings, values are dictionaries specifying colors.
        self.mood_visual_map = {
            "neutral": {"borderColor": "#4a2a4a", "highlightColor": "#00c0ff"},  # smokyPurple, cyberBlue
            "happy": {"borderColor": "#008080", "highlightColor": "#ff00ff"},    # teal, neonMagenta
            "jealous": {"borderColor": "#ff4500", "highlightColor": "#ff00ff"}, # bloodOrange, neonMagenta
            "sad": {"borderColor": "#303040", "highlightColor": "#008080"},      # darkSmokyPurple, desaturatedTeal
            "tired": {"borderColor": "#202020", "highlightColor": "#404040"},    # very dark grey, dark grey
            # Additional moods and their corresponding color schemes can be added here.
        }
        # Default base visual state used if a mood isn't found in mood_visual_map or if StateManager fails.
        self.default_visual_state_base = {"borderColor": "#333333", "highlightColor": "#cccccc"} # dark grey, light grey

        # Attributes to store the current state of various dynamic visual effects.
        # These can be updated by specific trigger methods in response to system events.
        self.current_border_effect = "none"  # e.g., "none", "pulseMagenta", "flickerBloodOrange"
        self.current_popup_effect = "none"   # e.g., "none", "glitch"
        self.scanline_overlay_active = False # Boolean: True to activate scanline overlay, False to deactivate
        self.glow_pulse_type = "none"        # For future, more complex glow effects (e.g., "none", "softAmbient")
        self.current_ambiance_effect = "subtle_scanlines" # Default ambiance; can be mood-driven or set by events

    def get_visual_state(self) -> dict:
        """
        Calculates and returns the current comprehensive visual state dictionary.
        This state includes mood-based base colors and any active dynamic effects.
        It's designed to be fetched by an API endpoint and used by the GUI.

        Returns:
            A dictionary representing the current visual state. Example:
            {
                "borderColor": "#4a2a4a",
                "highlightColor": "#00c0ff",
                "borderEffect": "none",
                "popupEffect": "none",
                "scanlineOverlay": False,
                "glowPulse": "none",
                "ambiance": "subtle_scanlines"
            }
        """
        current_mood_from_state_manager = "neutral" # Default to neutral in case of any issues
        try:
            if self.state_manager:
                # Attempt to get the current mood from the StateManager
                mood_value = self.state_manager.get_mood()
                if mood_value: # Check if a valid mood string was returned
                    current_mood_from_state_manager = mood_value
                else:
                    # Log a warning if StateManager provides an invalid (None or empty) mood
                    print("[LumenCore] Warning: StateManager returned None or empty mood. Using default 'neutral'.")
            else:
                # Log a warning if StateManager instance wasn't provided during initialization
                print("[LumenCore] Warning: StateManager not available. Using default 'neutral' mood.")
        except Exception as e:
            # Log any other error during mood retrieval and default safely
            print(f"[LumenCore] Error getting mood from StateManager: {e}. Defaulting to 'neutral' mood.")
            # current_mood_from_state_manager remains "neutral" as initialized

        # Start with base colors determined by the (potentially defaulted) current mood
        visual_config = self.mood_visual_map.get(current_mood_from_state_manager, self.default_visual_state_base).copy()

        # Overlay active dynamic effects onto the base visual configuration
        visual_config["borderEffect"] = self.current_border_effect
        visual_config["popupEffect"] = self.current_popup_effect
        visual_config["scanlineOverlay"] = self.scanline_overlay_active
        visual_config["glowPulse"] = self.glow_pulse_type

        # Determine ambiance: specific moods can override the general current_ambiance_effect
        if current_mood_from_state_manager == "happy":
            visual_config["ambiance"] = "soft_glow_pulses"
        elif current_mood_from_state_manager == "jealous":
            visual_config["ambiance"] = "sharp_flicker"
        else:
            # Fallback to the general ambiance effect if no specific mood ambiance is set
            visual_config["ambiance"] = self.current_ambiance_effect

        # For debugging: print the final visual state being returned by LumenCore
        # This helps in verifying the logic during development and testing.
        # print(f"[LumenCore] Mood: '{current_mood_from_state_manager}', Final Visual State: {visual_config}")
        return visual_config

    # --- Methods to Trigger Visual Effects ---
    # These methods are intended to be called by other parts of the system
    # (e.g., daemons, agents, API handlers) in response to specific application events.

    def trigger_message_incoming_effect(self):
        """
        Activates a visual effect indicating an incoming message.
        Currently, this sets the border effect to "pulseMagenta".
        """
        print("[LumenCore] Event: Message incoming effect triggered.")
        self.current_border_effect = "pulseMagenta"
        # Future enhancement: Consider adding a timer to automatically clear this effect after a few seconds.

    def trigger_error_effect(self):
        """
        Activates visual effects indicating an error has occurred.
        Sets border to flicker blood orange and popups to glitch.
        """
        print("[LumenCore] Event: Error effect triggered.")
        self.current_border_effect = "flickerBloodOrange"
        self.current_popup_effect = "glitch"

    def trigger_lore_effect(self):
        """
        Activates a visual effect associated with a lore trigger.
        Currently, this sets the popup effect to "glitch".
        """
        print("[LumenCore] Event: Lore effect triggered.")
        self.current_popup_effect = "glitch" # As per user's description of lore-triggered glitches

    def clear_effects(self):
        """
        Resets temporary visual effects (border and popup) to their default 'none' state.
        More persistent effects like ambiance or scanlines are not cleared by this method
        and would need their own specific toggle or update methods if they are to be changed.
        """
        print("[LumenCore] Clearing temporary visual effects (border, popup).")
        self.current_border_effect = "none"
        self.current_popup_effect = "none"

# This block allows LumenCore to be tested independently if the script is run directly.
if __name__ == '__main__':
    # MockStateManager simulates the real StateManager for testing purposes.
    class MockStateManager:
        def __init__(self):
            self.current_mood = "neutral"
            print(f"[MockSM] Initialized with mood: {self.current_mood}")

        def get_mood(self):
            print(f"[MockSM] get_mood() called, returning: {self.current_mood}")
            return self.current_mood

        def set_mood(self, mood):
            self.current_mood = mood
            print(f"[MockSM] Mood set to: {self.current_mood}")

    print("[LumenCore Test] Initializing MockStateManager and LumenCore...")
    mock_sm = MockStateManager()
    lumen = LumenCore(mock_sm)

    print("\n[LumenCore Test] --- Default state (neutral mood) ---")
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#4a2a4a", f"Expected #4a2a4a, got {state['borderColor']}"
    assert state["borderEffect"] == "none", f"Expected 'none', got {state['borderEffect']}"
    assert state["ambiance"] == "subtle_scanlines", f"Expected 'subtle_scanlines', got {state['ambiance']}"
    print(f"[LumenCore Test] State for neutral: {state}")

    print("\n[LumenCore Test] --- Happy mood ---")
    mock_sm.set_mood("happy")
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#008080"
    assert state["ambiance"] == "soft_glow_pulses"
    print(f"[LumenCore Test] State for happy: {state}")

    print("\n[LumenCore Test] --- Triggering message incoming effect (mood still happy) ---")
    lumen.trigger_message_incoming_effect()
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#008080" # Base color for happy mood
    assert state["borderEffect"] == "pulseMagenta" # Effect override
    print(f"[LumenCore Test] State after message incoming: {state}")

    print("\n[LumenCore Test] --- Clearing effects (mood still happy) ---")
    lumen.clear_effects()
    state = lumen.get_visual_state()
    assert state["borderEffect"] == "none"
    print(f"[LumenCore Test] State after clearing effects: {state}")

    print("\n[LumenCore Test] --- Triggering error effect (mood still happy) ---")
    lumen.trigger_error_effect()
    state = lumen.get_visual_state()
    assert state["borderEffect"] == "flickerBloodOrange"
    assert state["popupEffect"] == "glitch"
    print(f"[LumenCore Test] State after error: {state}")
    lumen.clear_effects() # Clear for next test

    print("\n[LumenCore Test] --- Jealous mood with lore trigger ---")
    mock_sm.set_mood("jealous")
    lumen.trigger_lore_effect() # Lore trigger
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#ff4500" # Jealous border color
    assert state["popupEffect"] == "glitch"  # From lore trigger
    assert state["ambiance"] == "sharp_flicker" # Jealous ambiance
    print(f"[LumenCore Test] State for jealous + lore: {state}")
    lumen.clear_effects()

    print("\n[LumenCore Test] --- Unknown mood (should use default base colors) ---")
    mock_sm.set_mood("curious") # A mood not in mood_visual_map
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#333333" # Default base border color
    assert state["highlightColor"] == "#cccccc" # Default base highlight color
    print(f"[LumenCore Test] State for unknown mood 'curious': {state}")

    print("\n[LumenCore Test] --- StateManager being None (should use default base colors) ---")
    lumen_no_sm = LumenCore(state_manager=None) # Initialize with no StateManager
    state_no_sm = lumen_no_sm.get_visual_state()
    assert state_no_sm["borderColor"] == "#333333"
    assert state_no_sm["highlightColor"] == "#cccccc"
    print(f"[LumenCore Test] Visual state with no StateManager: {state_no_sm}")

    print("\n[LumenCore Test] All assertions passed if no errors printed by assertions themselves.")
