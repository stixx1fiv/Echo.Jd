import os
import ast

def scan_for_daemon_candidates(folder_path):
    candidates = []

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, "r") as f:
                    file_content = f.read()

                try:
                    tree = ast.parse(file_content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ClassDef):
                            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                            if any(method in methods for method in ["run", "start", "stop"]):
                                candidates.append(file_path)
                except SyntaxError:
                    print(f"Syntax error in file: {file_path}")

    return candidates

# Example usage
if __name__ == "__main__":
    folder_path = "path/to/your/daemon/folder"  # 👈 Replace this with your actual path
    daemon_candidates = scan_for_daemon_candidates(folder_path)

    print("Files that could be refactored to use BaseDaemon:")
    for candidate in daemon_candidates:
        print(candidate)
