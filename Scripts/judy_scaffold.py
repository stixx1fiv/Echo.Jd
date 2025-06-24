import os
from datetime import datetime

# Define your full, updated project skeleton here
project_structure = {
    "brain": {
        "agents": {},
        "core": {},
        "daemons": {
            "heartbeat_daemon.py": "",
            "memory_daemon.py": "",
            "state_manager.py": "",
            "wine_daemon.py": "",
        },
        "memory": {
            "logs": {},
            "lore": {
                "core_lore.json": "",
                "event_lore.json": "",
            },
            "memories": {},
        },
        "plugins": {},
    },
    "gui": {
        "assets": {
            "images": {},
            "animations": {},
        },
        "templates": {},
        "widgets": {},
    },
    "api_gateway": {
        "routes": {},
        "plugins": {},
    },
    "user_data": {},  # watch folder for drops
    "logs": {},
    "scripts": {},
    "tests": {},
    "docs": {},
}

# Short folder descriptions
folder_descriptions = {
    "agents": "Houses routing and coordination agents like JalenAgent.",
    "core": "Core utilities and services for Judy's internal operations.",
    "daemons": "Background threads that handle system processes and monitoring.",
    "memory": "Memory files, logs, and lore management modules.",
    "plugins": "Optional integrations and external data hooks.",
    "assets": "GUI visual assets like images and animations.",
    "templates": "GUI layout templates and HTML/JS structures.",
    "widgets": "Custom GUI widgets and components.",
    "routes": "Local API endpoint definitions for Judy's gateway.",
    "logs": "Log files and system event records.",
    "scripts": "One-off or maintenance scripts for system management.",
    "tests": "Unit and integration test files.",
    "docs": "Project documentation and architecture notes.",
    "user_data": "Dropzone for files and messages you want Judy to see."
}

def create_structure(base_path, structure, log_lines):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            log_lines.append(f"[DIR] {path}")
            # Create README.md with description if available
            desc = folder_descriptions.get(name, "No description available for this folder.")
            readme_path = os.path.join(path, "README.md")
            with open(readme_path, 'w') as readme:
                readme.write(f"# {name}\n\n{desc}\n")
            log_lines.append(f"      → README.md created in {path}")
            create_structure(path, content, log_lines)
        else:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w') as f:
                f.write(content)
            log_lines.append(f"[FILE] {path}")

if __name__ == '__main__':
    base_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    log_file_path = os.path.join(base_directory, "setup_log.txt")
    log_lines = []
    log_lines.append(f"\n=== Judy Scaffold Run: {datetime.now()} ===\n")

    create_structure(base_directory, project_structure, log_lines)

    with open(log_file_path, 'a', encoding='utf-8') as log_file:
        log_file.write('\n'.join(log_lines))

    print("🍷✨ Project scaffold complete! Check 'setup_log.txt' for details.")
