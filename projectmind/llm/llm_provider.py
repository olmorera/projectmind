# llama_provider.py

import os
from llama_cpp import Llama
from loguru import logger
from projectmind.db.models.llm_config import LLMConfig
from projectmind.db.models.llm_model import LLMModel


class LlamaProvider:
    def __init__(self, config: LLMConfig, model: LLMModel):
        self.config = config
        self.model = model

        if model.provider != "llama":
            raise ValueError(f"Invalid provider for llama.cpp: {model.provider}")
        if not os.path.exists(model.model):
            raise FileNotFoundError(f"Model file not found at: {model.model}")

        logger.info(f"🧠 Initializing llama.cpp model: {model.name}")

        # Extraer parámetros desde el modelo (con fallback)
        llama_args = {
            "model_path": model.model,
            "chat_format": model.chat_format or "llama-2",
            "n_ctx": model.n_ctx or 4096,
            "n_threads": model.n_threads or os.cpu_count(),
            "n_threads_batch": model.n_threads or os.cpu_count(),
            "n_batch": model.n_batch or 64,
            "n_ubatch": model.n_batch or 64,
            "use_mmap": model.use_mmap if model.use_mmap is not None else True,
            "use_mlock": model.use_mlock if model.use_mlock is not None else False,
            "numa": model.numa or 1,
            "rope_scaling_type": model.rope_scaling_type or 2,
            "logits_all": model.logits_all if model.logits_all is not None else False,
            "embedding": model.embedding if model.embedding is not None else False,
            "offload_kqv": model.offload_kqv if model.offload_kqv is not None else False,
            "low_vram": model.low_vram if model.low_vram is not None else False,
            "f16_kv": model.f16_kv if model.f16_kv is not None else False,
            "verbose": model.verbose if model.verbose is not None else False
        }

        self.llm = Llama(**llama_args)

        self.temperature = config.temperature or 0.7
        self.max_tokens = config.max_tokens or 1024
        self.top_p = config.top_p or 1.0
        self.stop_tokens = self._parse_stop_tokens(config.stop_tokens)

    def generate(self, prompt: str) -> str:
        logger.debug("📝 Prompt enviado al modelo llama.cpp")
        response = self.llm(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            stop=self.stop_tokens
        )
        output = response["choices"][0]["text"].strip()
        logger.debug("✅ Respuesta recibida del modelo llama.cpp")
        return output

    def _parse_stop_tokens(self, stop_tokens_raw: str):
        if not stop_tokens_raw:
            return None
        return [s.strip() for s in stop_tokens_raw.split(",")]
