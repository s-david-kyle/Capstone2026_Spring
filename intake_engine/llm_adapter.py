from abc import ABC, abstractmethod


class BaseLLMAdapter(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        raise NotImplementedError


class GemmaGGUFAdapter(BaseLLMAdapter):
    def __init__(
        self,
        model_path: str,
        n_ctx: int = 2048,
        n_gpu_layers: int = -1,
        max_tokens: int = 80,
        temperature: float = 0.2,
    ):
        from llama_cpp import Llama

        self.max_tokens = max_tokens
        self.temperature = temperature

        self.llm = Llama(
            model_path = model_path,
            n_ctx = n_ctx,
            n_gpu_layers = n_gpu_layers,
            verbose = False,
        )

    def generate(self, prompt: str) -> str:
        result = self.llm(
            prompt,
            max_tokens = self.max_tokens,
            temperature = self.temperature,
            echo = False,
            stop = ["Output:", "Reasoning:"],
        )

        text = result["choices"][0]["text"].strip()

        if not text:
            raise ValueError("GemmaGGUFAdapter returned empty text")

        return text


class OllamaAdapter(BaseLLMAdapter):
    def __init__(
        self,
        model_name: str,
        base_url: str = "http://localhost:11434",
        max_tokens: int = 80,
        temperature: float = 0.2,
    ):
        import ollama

        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self.max_tokens = max_tokens
        self.temperature = temperature

        self.client = ollama.Client(host = self.base_url)

    def generate(self, prompt: str) -> str:
        response = self.client.generate(
            model = self.model_name,
            prompt = prompt,
            options = {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        )

        text = response.get("response", "").strip()

        if not text:
            raise ValueError("OllamaAdapter returned empty text")

        return text


def create_llm_adapter(config: dict) -> BaseLLMAdapter:
    backend = config["backend"]

    if backend == "llama_cpp":
        return GemmaGGUFAdapter(
            model_path = config["gguf_model_path"],
            n_ctx = config["n_ctx"],
            n_gpu_layers = config["n_gpu_layers"],
            max_tokens = config["max_tokens"],
            temperature = config["temperature"],
        )

    if backend == "ollama":
        return OllamaAdapter(
            model_name = config["ollama_model_name"],
            base_url = config["ollama_base_url"],
            max_tokens = config["max_tokens"],
            temperature = config["temperature"],
        )

    raise ValueError(f"Unsupported LLM backend: {backend}")