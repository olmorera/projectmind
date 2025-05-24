# projectmind/llm/llama_provider.py

import os
from llama_cpp import Llama
from projectmind.models.chat_message import ChatMessage
from projectmind.db.models.llm_model import LLMModel
from projectmind.db.models.llm_config import LLMConfig
from projectmind.llm.llama_loader import load_llama_cpp_library
from loguru import logger

load_llama_cpp_library()

def _safe_bool(value: bool | None, default: bool = False) -> bool:
    return default if value is None else value

class LlamaProvider:
    def __init__(self, config: LLMConfig, model: LLMModel):
        self.config = config
        self.model = model

        if model.provider != "llama":
            raise ValueError(f"❌ Invalid provider: {model.provider}")
        if not model.model or not os.path.isfile(model.model):
            raise FileNotFoundError(f"❌ Model file not found: {model.model}")

        logger.info(f"🧠 Loading GGUF model: {os.path.basename(model.model)}")

        self.llm = Llama(
            model_path=model.model,
            chat_format=model.chat_format or None,
            n_ctx=model.n_ctx or 4096,
            n_threads=model.n_threads or os.cpu_count(),
            n_threads_batch=model.n_threads or os.cpu_count(),
            n_batch=model.n_batch or 64,
            n_ubatch=model.n_batch or 64,
            use_mmap=_safe_bool(model.use_mmap, True),
            use_mlock=_safe_bool(model.use_mlock, False),
            numa=model.numa or 1,
            rope_scaling_type=model.rope_scaling_type or 1,
            f16_kv=_safe_bool(model.f16_kv),
            low_vram=_safe_bool(model.low_vram),
            offload_kqv=_safe_bool(model.offload_kqv),
            embedding=_safe_bool(model.embedding),
            logits_all=_safe_bool(model.logits_all),
            verbose=_safe_bool(model.verbose),
            mixture_of_experts=_safe_bool(getattr(model, "mixture_of_experts", False)),
        )

        self.temperature = config.temperature or 0.7
        self.max_tokens = config.max_tokens or 1024
        self.top_p = config.top_p or 1.0
        self.stop_tokens = config.stop_tokens or []

        for k, v in self.llm.metadata.items():
            logger.debug(f"{k}: {v}")

    def chat(self, messages: list[ChatMessage | dict]) -> str:
        logger.debug("🗨️ Generating response using structured chat format")

        formatted_messages = [m.dict() if isinstance(m, ChatMessage) else ChatMessage(**m).dict() for m in messages]

        logger.debug({
            "messages": formatted_messages,
            "chat_format": self.model.chat_format,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "stop_tokens": self.stop_tokens,
        })

        try:
            response = self.llm.create_chat_completion(
                messages=formatted_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                top_p=self.top_p,
                stop=self.stop_tokens or None,
            )
            return response["choices"][0]["message"]["content"].strip()
        except Exception as e:
            logger.error(f"❌ Chat generation failed: {e}")
            return f"⚠️ Failed to generate response: {str(e)}"
