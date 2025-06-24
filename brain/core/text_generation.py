import threading
from llama_cpp import Llama

class TextGeneration:
    def __init__(self, model_path=None):
        self.model_path = model_path or r"C:\\Users\\cnorthington\\xxEcho.JD\\models\\mistral-7b-v0.1.Q4_0.gguf"
        print(f"[TextGeneration] Loading model from {self.model_path} with GPU acceleration if available...")
        try:
            self.model = Llama(model_path=self.model_path, n_gpu_layers=20)
        except TypeError:
            self.model = Llama(model_path=self.model_path)
        self.lock = threading.Lock()

    def generate(self, prompt, max_tokens=150, temperature=0.3):
        with self.lock:
            print(f"\n[TextGeneration] Prompt being sent:\n{prompt}\n")
            response = self.model(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["You:", "Stixx:", "\nYou:", "\nStixx:", "\n\n", "User:", "\nUser:"]
            )
            result = response['choices'][0]['text'].strip()
            print(f"[TextGeneration] Generated response: {result}")
            return result

    def generate_async(self, prompt, callback, max_tokens=150, temperature=0.3):
        def worker():
            try:
                result = self.generate(prompt, max_tokens=max_tokens, temperature=temperature)
            except Exception as e:
                result = f"Error during generation: {str(e)}"
            callback(result)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
        return thread

    def switch_model(self, model_path, n_gpu_layers=20):
        with self.lock:
            try:
                print(f"[TextGeneration] Switching to model: {model_path}")
                self.model = Llama(model_path=model_path, n_gpu_layers=n_gpu_layers)
                self.model_path = model_path
                print(f"[TextGeneration] Model switched successfully.")
            except Exception as e:
                print(f"[TextGeneration] Failed to switch model: {e}")
