import os
import sys
import threading

# This line attempts to add the project\'s root directory (one level up from \'brain\')
# to the Python path. This can help ensure that imports like \'from brain.core...\'\n# work correctly when this script might be run in different contexts, although\n# for typical FastAPI execution via uvicorn from the project root, this might be redundant.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from brain.core.state_manager import StateManager # Import necessary for type hinting and interaction
from brain.daemons.heartbeat_daemon import HeartbeatDaemon # Import HeartbeatDaemon for type hinting and interaction

class LumenCore:
    """
    Manages and calculates the visual state (colors, effects) for Judy\'s presence.
    This state is primarily based on Judy\'s current mood (obtained from StateManager)
    and can also be influenced by specific triggered events (e.g., errors, new messages),
    and now, the heartbeat daemon's vital signs.
    The visual state is intended to be consumed by a GUI or other rendering component
    to dynamically alter the application\'s appearance.
    """
    def __init__(self, state_manager: StateManager, heartbeat_daemon: HeartbeatDaemon = None):
        """
        Initializes the LumenCore.

        Args:
            state_manager: An instance of StateManager, used to fetch the current
                           mood and potentially other system states that might influence visuals.
            heartbeat_daemon: An optional instance of HeartbeatDaemon, used to receive
                              vital sign updates and influence visuals based on system health.
        """
        self.state_manager = state_manager
        self.heartbeat_daemon = heartbeat_daemon # Store the heartbeat daemon instance
        self.current_vital_sign = 0.0 # Initialize vital sign

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

        # Subscribe to heartbeat daemon if provided
        if self.heartbeat_daemon:
            self.heartbeat_daemon.subscribe(self.on_heartbeat)
            print("[LumenCore] Subscribed to HeartbeatDaemon.")


    def on_heartbeat(self, vital_sign):
        self.current_vital_sign = vital_sign
        if vital_sign > 0.9:
            self.current_border_effect = "pulseMagenta_frenzy"  # extra hype mode
        elif vital_sign > 0.7:
            self.current_border_effect = "pulseMagenta"  # active pulse
        elif vital_sign < 0.3:
            self.current_border_effect = "pulseDim"  # low energy pulse
        else:
            self.current_border_effect = "none"


    def trigger_message_incoming_effect(self):
        print("[LumenCore] Event: Message incoming effect triggered.")
        self.current_border_effect = "pulseMagenta"

        def clear():
            self.clear_effects()
            print("[LumenCore] Message incoming effect cleared.")
        timer = threading.Timer(3.0, clear)
        timer.start()


    def get_visual_state(self) -> dict:
        """
        Calculates and returns the current comprehensive visual state dictionary.
        This state includes mood-based base colors and any active dynamic effects,
        including those influenced by the heartbeat daemon.
        It\'s designed to be fetched by an API endpoint and used by the GUI.

        Returns:
            A dictionary representing the current visual state. Example:
            {
                "borderColor": "#4a2a4a",
                "highlightColor": "#00c0ff",
                "borderEffect": "none",
                "popupEffect": "none",
                "scanlineOverlay": False,
                "glowPulse": "none",
                "ambiance": "subtle_scanlines",
                "vitalSign": 0.5 # Added vital sign to the state for potential GUI display
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
            # current_mood_from_state_manager remains \"neutral\" as initialized

        # Start with base colors determined by the (potentially defaulted) current mood
        visual_config = self.mood_visual_map.get(current_mood_from_state_manager, self.default_visual_state_base).copy()

        # Overlay active dynamic effects onto the base visual configuration
        # The borderEffect is now also influenced by the heartbeat
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

        # Add the current vital sign to the visual state
        visual_config["vitalSign"] = self.current_vital_sign

        # For debugging: print the final visual state being returned by LumenCore
        # This helps in verifying the logic during development and testing.
        # print(f"[LumenCore] Mood: '{current_mood_from_state_manager}', Final Visual State: {visual_config}")
        return visual_config


    # --- Methods to Trigger Visual Effects ---
    # These methods are intended to be called by other parts of the system
    # (e.g., daemons, agents, API handlers) in response to specific application events.

    # def trigger_message_incoming_effect(self):
    #     """
    #     Activates a visual effect indicating an incoming message.
    #     Currently, this sets the border effect to "pulseMagenta".
    #     """
    #     print("[LumenCore] Event: Message incoming effect triggered.")
    #     self.current_border_effect = "pulseMagenta"
    #     # Future enhancement: Consider adding a timer to automatically clear this effect after a few seconds.

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

    # MockHeartbeatDaemon simulates the real HeartbeatDaemon for testing.
    class MockHeartbeatDaemon:
        def __init__(self):
            self.subscribers = []
            print("[MockHBD] Initialized.")

        def subscribe(self, callback):
            self.subscribers.append(callback)
            print("[MockHBD] Callback subscribed.")

        # Simulate a heartbeat with vital sign
        def simulate_heartbeat(self, vital_sign):
            print(f"[MockHBD] Simulating heartbeat with vital sign: {vital_sign}")
            for callback in self.subscribers:
                callback(vital_sign)

    print("[LumenCore Test] Initializing MockStateManager, MockHeartbeatDaemon, and LumenCore...")
    mock_sm = MockStateManager()
    mock_hbd = MockHeartbeatDaemon()
    lumen = LumenCore(mock_sm, mock_hbd)

    print("\n[LumenCore Test] --- Default state (neutral mood) ---")
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#4a2a4a", f"Expected #4a2a4a, got {state['borderColor']}"
    assert state["borderEffect"] == "none", f"Expected 'none', got {state['borderEffect']}"
    assert state["ambiance"] == "subtle_scanlines", f"Expected 'subtle_scanlines', got {state['ambiance']}"
    assert state["vitalSign"] == 0.0, f"Expected 0.0, got {state['vitalSign']}"
    print(f"[LumenCore Test] State for neutral: {state}")

    print("\n[LumenCore Test] --- Simulating heartbeat with high vital sign (0.9) ---")
    mock_hbd.simulate_heartbeat(0.9)
    state = lumen.get_visual_state()
    assert state["vitalSign"] == 0.9
    assert state["borderEffect"] == "pulseMagenta_frenzy" # Updated assertion for frenzy mode
    print(f"[LumenCore Test] State after high vital sign: {state}")

    print("\n[LumenCore Test] --- Simulating heartbeat with low vital sign (0.3) ---")
    mock_hbd.simulate_heartbeat(0.3)
    state = lumen.get_visual_state()
    assert state["vitalSign"] == 0.3
    assert state["borderEffect"] == "pulseDim" # Updated assertion for dim pulse
    print(f"[LumenCore Test] State after low vital sign: {state}")

    print("\n[LumenCore Test] --- Happy mood with high vital sign ---\")
    mock_sm.set_mood("happy")
    mock_hbd.simulate_heartbeat(0.8)
    state = lumen.get_visual_state()
    assert state["borderColor"] == "#008080" # Base color for happy mood
    assert state["ambiance"] == "soft_glow_pulses"
    assert state["vitalSign"] == 0.8
    assert state["borderEffect"] == "pulseMagenta" # Effect override from vital sign
    print(f"[LumenCore Test] State for happy + high vital sign: {state}")

    print("\n[LumenCore Test] --- Triggering message incoming effect ---")
    lumen.trigger_message_incoming_effect()
    state = lumen.get_visual_state()
    assert state["borderEffect"] == "pulseMagenta"
    print(f"[LumenCore Test] State after message incoming trigger: {state}")
    # Note: The clear will happen after 3 seconds due to the timer

    print("\n[LumenCore Test] All assertions passed if no errors printed by assertions themselves.")
