# projectmind/llm/llama_provider.py

import os
# 🔁 Usar tu compilación local de llama.cpp
os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/bin/libllama.so"
from llama_cpp import Llama
from projectmind.db.models.llm_model import LLMModel
from projectmind.db.models.llm_config import LLMConfig
from loguru import logger


class LlamaProvider:
    def __init__(self, config: LLMConfig, model: LLMModel):
        self.config = config
        self.model = model

        if model.provider != "llama":
            raise ValueError(f"Invalid provider: {model.provider}")

        if not model.model or not os.path.exists(model.model):
            raise FileNotFoundError(f"Model file not found: {model.model}")

        logger.info(f"🧠 Loading GGUF model: {model.name}")

        self.llm = Llama(
            model_path=model.model,
            chat_format=model.chat_format or "llama-2",
            n_ctx=model.n_ctx or 4096,
            n_threads=model.n_threads or os.cpu_count(),
            n_threads_batch=model.n_threads or os.cpu_count(),
            n_batch=model.n_batch or 64,
            n_ubatch=model.n_batch or 64,
            use_mmap=model.use_mmap if model.use_mmap is not None else True,
            use_mlock=model.use_mlock if model.use_mlock is not None else False,
            numa=model.numa or 1,
            rope_scaling_type=model.rope_scaling_type or 1,
            f16_kv=model.f16_kv or False,
            low_vram=model.low_vram or False,
            offload_kqv=model.offload_kqv or False,
            embedding=model.embedding or False,
            logits_all=model.logits_all or False,
            verbose=model.verbose or False
        )

        self.temperature = config.temperature or 0.7
        self.max_tokens = config.max_tokens or 1024
        self.top_p = config.top_p or 1.0
        self.stop_tokens = [s.strip() for s in (config.stop_tokens or "").split(",") if s.strip()] or ["</s>", "```", "\n\n"]

    def generate(self, prompt: str) -> str:
        logger.debug("📝 Generating response with llama.cpp")
        response = self.llm(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            stop=self.stop_tokens
        )
        return response["choices"][0]["text"].strip()
