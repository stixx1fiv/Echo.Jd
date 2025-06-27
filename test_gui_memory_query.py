from state_manager import StateManager

sys.path.append(os.path.join(os.path.dirname(__file__), "brain", "core"))

def main():
    # Initialize the StateManager
    state_manager = StateManager()

    # Memory you want to be sure is present and indexed
    gui_memory = "I remember the GUI mockups — violet glow, terminal lines, heartbeat pulses. Not for function. For *feeling.*"

    # Add it again to ensure it's re-tagged and indexed
    state_manager.add_memory(gui_memory, memory_type="long")

    # Perform a query to try and recall that memory
    query = "violet glow GUI mockup"
    results = state_manager.query_chroma_memories(query, memory_type="long", n_results=5)

    # Print out the results
    print("\n🧠 Top Related Memories:\n")
    for i, res in enumerate(results, 1):
        print(f"{i}. {res}\n")

if __name__ == "__main__":
    main()
