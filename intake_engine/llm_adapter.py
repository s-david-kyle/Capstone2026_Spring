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


class ClaudeHaikuAdapter(BaseLLMAdapter):
    """
    Uses Claude Haiku via the Anthropic API for reliable JSON extraction.
    Designed to be used as the extractor backend while keeping a local
    model (Gemma/Ollama) for question generation.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-haiku-4-5-20251001",
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ):
        import anthropic

        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = anthropic.Anthropic(api_key = api_key)

    def generate(self, prompt: str) -> str:
        response = self.client.messages.create(
            model = self.model,
            max_tokens = self.max_tokens,
            temperature = self.temperature,
            messages = [{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()

        if not text:
            raise ValueError("ClaudeHaikuAdapter returned empty text")

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

    if backend == "claude_haiku":
        from intake_engine.config import API_KEYS
        return ClaudeHaikuAdapter(
            api_key = API_KEYS["anthropic"],
            model = config.get("claude_model", "claude-haiku-4-5-20251001"),
            max_tokens = config.get("claude_max_tokens", 1024),
            temperature = config.get("temperature", 0.0),
        )

    raise ValueError(f"Unsupported LLM backend: {backend}")


def create_extraction_adapter(config: dict) -> BaseLLMAdapter:
    """
    Always returns a ClaudeHaikuAdapter for extraction regardless of
    the main backend. This gives reliable JSON output while keeping
    the local model for question generation.
    """
    from intake_engine.config import API_KEYS
    return ClaudeHaikuAdapter(
        api_key = API_KEYS["anthropic"],
        model = config.get("claude_model", "claude-haiku-4-5-20251001"),
        max_tokens = 1024,
        temperature = 0.0,
    )
