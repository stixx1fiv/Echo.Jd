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
        n_gpu_layers = 20 if n_gpu_layers is None else n_gpu_layers

        if not resolved_model_path:
            raise ValueError(
                "Model path could not be determined. Please provide `model_path`, set the "
                "`JUDY_MODEL_PATH` environment variable, or add it to `config/config.yaml`."
            )

        # If the provided path does not exist, attempt a naive fallback search in
        # the local `models/` directory for any *.gguf file. This spares new
        # users from having to modify configuration files immediately after
        # cloning the repo.
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

        self.model_path = resolved_model_path
        self.n_gpu_layers = n_gpu_layers
        self.log_prompts = log_prompts # Store the log_prompts preference

        print(
            f"[TextGeneration] Loading model from {self.model_path} (n_gpu_layers={self.n_gpu_layers})..."
        )

        # Attempt GPU offload, fallback gracefully if unsupported by the platform or llama.cpp version
        try:
            self.model = Llama(model_path=self.model_path, n_gpu_layers=self.n_gpu_layers)
        except TypeError:
            # Older versions of llama.cpp might not accept n_gpu_layers
            self.model = Llama(model_path=self.model_path)
        except Exception as e: # Catch other potential model loading errors
            print(f"[TextGeneration] Critical error loading model: {e}. Text generation will likely fail.")
            self.model = None # Ensure model is None if loading fails catastrophically


        self.lock = threading.Lock()

    def generate(self, prompt, max_tokens=150, temperature=0.3):
        with self.lock:
            if self.log_prompts:
                print(f"\n[TextGeneration] Prompt being sent:\n{prompt}\n")
            
            if self.model is None:
                # This case should ideally be handled before calling generate,
                # or by how JalenAgent handles a None model from TextGeneration.
                # For now, return a clear error message.
                result = "[TextGeneration Error: Model not available]"
            else:
                try:
                    response = self.model(
                        prompt=prompt,
                        max_tokens=max_tokens,
                        temperature=temperature,
                        stop=["You:", "Stixx:", "\nYou:", "\nStixx:", "User:", "\nUser:"]
                    )
                    result = response['choices'][0]['text'].strip()
                except Exception as e:
                    result = f"[TextGeneration Error: {e}]"

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
                self.model = Llama(model_path=model_path, n_gpu_layers=n_gpu_layers)
                self.model_path = model_path
                self.n_gpu_layers = n_gpu_layers
                print("[TextGeneration] Model switched successfully.")
            except Exception as e:
                print(f"[TextGeneration] Failed to switch model: {e}")
