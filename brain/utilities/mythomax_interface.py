import subprocess
import threading

class MythomaxInterface:
    def __init__(self, cli_path="mythomax-cli", max_tokens=150, timeout=15):
        self.cli_path = cli_path
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.lock = threading.Lock()  # For thread safety if needed

    def generate_text(self, prompt):
        """
        Sends prompt to Mythomax CLI (or API) and returns the generated text.
        Handles errors gracefully.
        """
        with self.lock:
            try:
                # Example subprocess call - adapt CLI args for your actual Mythomax tool
                result = subprocess.run(
                    [self.cli_path, "--prompt", prompt, "--max_tokens", str(self.max_tokens)],
                    capture_output=True, text=True, timeout=self.timeout
                )
                if result.returncode == 0:
                    return result.stdout.strip()
                else:
                    print("[MythomaxInterface] CLI error:", result.stderr)
                    return "Hmm... my brain hit a snag."
            except Exception as e:
                print("[MythomaxInterface] Exception:", e)
                return "Oops, I'm tangled in the code. Try again?"

