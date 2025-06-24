from brain.core.state_manager import StateManager
from brain.core.text_generation import TextGeneration
from brain.core.text_response_manager import TextResponseManager

def main():
    print("[🌹] Judy System Booting...")

    # Init core systems
    state_manager = StateManager()
    text_generator = TextGeneration()
    response_manager = TextResponseManager(state_manager, text_generator)

    print("[✅] Systems online. Judy's listening...")

    while True:
        user_input = input("\n🟣 You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("[💤] Shutting down Judy.")
            break

        response = response_manager.generate_response(user_input)
        print(f"\n🌹 Judy: {response}")

if __name__ == "__main__":
    main()
