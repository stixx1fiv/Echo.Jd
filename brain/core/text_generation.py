import threading
from llama_cpp import Llama  # type: ignore
import os
import glob
import yaml

class TextGeneration:
    """Wrapper around `llama_cpp.Llama` that adds simple concurrency control and configuration loading.

    The constructor will attempt to resolve the model path in the following order:

    1. The explicit ``model_path`` argument.
    2. An environment variable named ``JUDY_MODEL_PATH``.
    3. The ``config/config.yaml`` file under the key ``model_settings.model_path``.

    If none of the above yield a valid path, a ``ValueError`` is raised with a clear
    message. The same logic is used for ``n_gpu_layers`` (default **20** if not
    specified anywhere).
    """

    def __init__(self, model_path: str | None = None, n_gpu_layers: int | None = None, log_prompts: bool = False):
        # Store configuration but don't load model immediately (lazy loading)
        self.model_path = self._resolve_model_path(model_path, n_gpu_layers)
        self.n_gpu_layers = self._resolved_n_gpu_layers
        self.log_prompts = log_prompts
        
        # Model loading state
        self.model = None
        self.lock = threading.Lock()
        self._loading = False
        self._load_error = None
        
        print(f"[TextGeneration] Configured model: {self.model_path} (n_gpu_layers={self.n_gpu_layers})")
        print(f"[TextGeneration] Model will be loaded on first use (lazy loading)")

    def _resolve_model_path(self, model_path: str | None = None, n_gpu_layers: int | None = None):
        """Resolve model path and n_gpu_layers from various sources"""
        # 1) Explicit argument takes precedence
        resolved_model_path = model_path

        # 2) Environment variable
        if resolved_model_path is None:
            resolved_model_path = os.getenv("JUDY_MODEL_PATH")

        # 3) YAML configuration file
        if resolved_model_path is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
            config_path = os.path.join(project_root, "config", "config.yaml")
            if os.path.exists(config_path):
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        cfg = yaml.safe_load(f) or {}
                    resolved_model_path = cfg.get("model_settings", {}).get("model_path")
                    if n_gpu_layers is None:
                        n_gpu_layers = cfg.get("model_settings", {}).get("n_gpu_layers")
                except Exception as e:
                    print(f"[TextGeneration] Failed to read config.yaml: {e}")

        # Default n_gpu_layers fallback
        self._resolved_n_gpu_layers = 20 if n_gpu_layers is None else n_gpu_layers

        if not resolved_model_path:
            raise ValueError(
                "Model path could not be determined. Please provide `model_path`, set the "
                "`JUDY_MODEL_PATH` environment variable, or add it to `config/config.yaml`."
            )

        # If the provided path does not exist, attempt a naive fallback search in
        # the local `models/` directory for any *.gguf file.
        if not os.path.exists(resolved_model_path):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
            candidate_models = glob.glob(os.path.join(project_root, "models", "*.gguf"))
            if candidate_models:
                print(
                    f"[TextGeneration] Provided model path '{resolved_model_path}' not found. "
                    f"Falling back to detected model '{candidate_models[0]}'."
                )
                resolved_model_path = candidate_models[0]
            else:
                raise FileNotFoundError(
                    f"Model file '{resolved_model_path}' does not exist and no .gguf files were "
                    "found inside the project's 'models/' directory."
                )

        return resolved_model_path

    def _ensure_model_loaded(self):
        """Ensure the model is loaded, with thread-safe lazy loading"""
        if self.model is not None:
            return True
            
        if self._load_error is not None:
            print(f"[TextGeneration] Previous load error: {self._load_error}")
            return False
            
        if self._loading:
            # Another thread is already loading, wait for it
            import time
            while self._loading and self.model is None:
                time.sleep(0.1)
            return self.model is not None
            
        # This thread will load the model
        self._loading = True
        try:
            print(f"[TextGeneration] Loading model from {self.model_path} (n_gpu_layers={self.n_gpu_layers})...")
            
            # Attempt GPU offload, fallback gracefully if unsupported
            try:
                self.model = Llama(model_path=self.model_path, n_gpu_layers=self.n_gpu_layers)
                print(f"[TextGeneration] Model loaded successfully with GPU layers: {self.n_gpu_layers}")
            except TypeError:
                # Older versions of llama.cpp might not accept n_gpu_layers
                print(f"[TextGeneration] GPU layers not supported, falling back to CPU-only")
                self.model = Llama(model_path=self.model_path)
            except Exception as e:
                print(f"[TextGeneration] GPU loading failed ({e}), trying CPU-only...")
                try:
                    self.model = Llama(model_path=self.model_path)
                    print(f"[TextGeneration] Model loaded successfully on CPU")
                except Exception as cpu_error:
                    self._load_error = f"Failed to load model: {cpu_error}"
                    print(f"[TextGeneration] Critical error loading model: {self._load_error}")
                    return False
                    
            return True
            
        except Exception as e:
            self._load_error = str(e)
            print(f"[TextGeneration] Critical error loading model: {self._load_error}")
            return False
        finally:
            self._loading = False

    def generate(self, prompt, max_tokens=150, temperature=0.3):
        with self.lock:
            if not self._ensure_model_loaded():
                return f"[TextGeneration Error: {self._load_error or 'Model not available'}]"
            
            if self.log_prompts:
                print(f"\n[TextGeneration] Prompt being sent:\n{prompt}\n")
            
            try:
                response = self.model(
                    prompt=prompt,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                result = response['choices'][0]['text'].strip()
            except Exception as e:
                result = f"[TextGeneration Error: {e}]"
                print(f"[TextGeneration] Generation error: {e}")

            # Post-process to extract Judy's first answer and trim repeated chat turns.
            result = self._extract_first_assistant_response(result)

            if self.log_prompts:
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

    def switch_model(self, model_path: str, n_gpu_layers: int | None = None):
        """Hot-swap the underlying GGUF model at runtime."""
        n_gpu_layers = self.n_gpu_layers if n_gpu_layers is None else n_gpu_layers

        with self.lock:
            try:
                print(
                    f"[TextGeneration] Switching to model: {model_path} (n_gpu_layers={n_gpu_layers})"
                )
                # Reset loading state
                self._loading = False
                self._load_error = None
                self.model = None
                
                # Update paths
                self.model_path = model_path
                self.n_gpu_layers = n_gpu_layers
                
                # Load new model
                if self._ensure_model_loaded():
                    print("[TextGeneration] Model switched successfully.")
                else:
                    print("[TextGeneration] Failed to switch model.")
            except Exception as e:
                print(f"[TextGeneration] Failed to switch model: {e}")
                self._load_error = str(e)

    def is_ready(self):
        """Check if the model is ready for generation"""
        return self.model is not None and self._load_error is None

    def get_status(self):
        """Get current model status"""
        if self._loading:
            return "loading"
        elif self.model is not None:
            return "ready"
        elif self._load_error:
            return f"error: {self._load_error}"
        else:
            return "not_loaded"

    @staticmethod
    def _extract_first_assistant_response(text: str) -> str:
        """Return only Judy's first reply, discarding further chat turns.

        The model sometimes continues the conversation by emitting multiple
        user/assistant turns in one go. We want just the first assistant utterance.
        """
        import re

        # Normalize newlines to ensure consistent parsing
        text = text.replace("\r\n", "\n")

        # The text is the raw model output. We need to find where the *next* turn starts.
        # This could be a user turn or another assistant turn.
        stop_match = re.search(r"(?:\n|^)\s*###\s*(User|Assistant|System)", text, flags=re.IGNORECASE)
        if stop_match:
            text = text[:stop_match.start()]

        cleaned = text.strip()

        # If cleaning resulted in an empty string or still contains "###" markers, return
        # the original text (also stripped) so the caller at least sees something.
        if not cleaned or cleaned.startswith("###"):
            return text.strip()

        return cleaned