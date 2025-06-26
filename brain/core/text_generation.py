from llama_cpp import Llama

class TextGenerator:
    def __init__(self, model_path="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"):
        self.model_path = model_path
        self.llm = self.load_model()

    def load_model(self):
        return Llama(
            model_path=self.model_path,
            n_ctx=2048,
            n_batch=512,
            n_threads=8,
            n_gpu_layers=33,
            use_mlock=True,
            verbose=False
        )

    def generate(self, prompt, context=None, max_tokens=150, temperature=0.3):
        if context:
            formatted_context = "\n".join([f"[Memory] {item}" for item in context])
            prompt = f"{formatted_context}\n\n{prompt}"

        output = self.llm(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            echo=False
        )
        return output["choices"][0]["text"].strip()
