from brain.core.state_manager import StateManager

def main():
    # Initialize the StateManager
    state_manager = StateManager()

    # Memory you want to make sure is stored and indexed
    gui_memory = "I remember the GUI mockups — violet glow, terminal lines, heartbeat pulses. Not for function. For *feeling.*"

    # Add it again to make sure it's in ChromaDB
    state_manager.add_memory(gui_memory, memory_type="long")

    # Query to test if the memory can be recalled
    query = "violet glow GUI mockup"
    results = state_manager.query_chroma_memories(query, memory_type="long", n_results=5)

    # Print out any results
    print("\n🧠 Top Related Memories:\n")
    for i, res in enumerate(results, 1):
        print(f"{i}. {res}\n")

if __name__ == "__main__":
    main()
