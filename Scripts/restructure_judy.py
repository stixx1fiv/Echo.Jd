import os
import json

# Files to delete entirely (orphans, unused stubs)
files_to_delete = [
    "brain/daemons/state_manager.py"
]

# JSON files to reset to an empty structure
json_files_to_reset = [
    "brain/indexes/memory_index.json",
    "brain/memory/completed_tasks.json",
    "brain/memory/profiles/relationship_map.json",
    "brain/memory/task_queue.json",
    "brain/memory/tasks/task_queue.json",
    "brain/memory/tasks/active_tasks.json",
    "brain/memory/tasks/completed_tasks.json",
    "chronicles/notes/random_notes.json",
    "config/config.yaml",
    "config/mood_state.json",
    "config/prompt_frame.json",
    "config/scene_context.json",
    "lore/location_index.json",
    "lore/portal_theories.json",
    "lore/world_history.json",
    "runtime/timestamps.json"
]

# Clean JSON files with { } or [] based on original intent
def reset_json(filepath):
    if filepath.endswith(".yaml"):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write("# Empty YAML config")
    else:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump({}, f, indent=2)

# README.md files to empty or prune
readmes_to_clear = [
    "api_gateway/README.md",
    "api_gateway/plugins/README.md",
    "brain/README.md",
    "brain/memory/lore/README.md",
    "brain/memory/memories/README.md",
    "gui/README.md",
    "gui/assets/animations/README.md",
    "gui/assets/images/README.md",
    "gui/templates/README.md",
    "Scripts/README.md",
    "tests/README.md",
    "logs/README.md"
]

# Delete unused files
for file in files_to_delete:
    if os.path.exists(file):
        os.remove(file)
        print(f"[🗑️] Removed orphan file: {file}")

# Clean JSON files
for json_file in json_files_to_reset:
    if os.path.exists(json_file):
        reset_json(json_file)
        print(f"[📝] Reset JSON file: {json_file}")

# Clean READMEs
for readme in readmes_to_clear:
    if os.path.exists(readme):
        with open(readme, "w", encoding="utf-8") as f:
            f.write("# Placeholder — Customize me later.")
        print(f"[📖] Cleaned README: {readme}")

print("\n[✅] Repo restructure & cleanup complete.")
