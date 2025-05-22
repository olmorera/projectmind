import os
from llama_cpp import Llama
from projectmind.db.models.llm_model import LLMModel
from projectmind.db.models.llm_config import LLMConfig
from projectmind.llm.llama_loader import load_llama_cpp_library
from loguru import logger

# Load llama.cpp shared library
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

        # Config defaults
        threads = model.n_threads or os.cpu_count()
        batch = model.n_batch or 64
        context = model.n_ctx or 4096
        chat_format = model.chat_format or None

        # Log Llama init params
        logger.debug("⚙️ llama.cpp initialization parameters:")
        logger.debug({
            "model_path": model.model,
            "chat_format": chat_format,
            "n_ctx": context,
            "n_threads": threads,
            "n_batch": batch,
            "use_mmap": _safe_bool(model.use_mmap, True),
            "use_mlock": _safe_bool(model.use_mlock, False),
            "numa": model.numa or 1,
            "rope_scaling_type": model.rope_scaling_type or 1,
            "f16_kv": _safe_bool(model.f16_kv),
            "low_vram": _safe_bool(model.low_vram),
            "offload_kqv": _safe_bool(model.offload_kqv),
            "embedding": _safe_bool(model.embedding),
            "logits_all": _safe_bool(model.logits_all),
            "verbose": _safe_bool(model.verbose),
            "mixture_of_experts": _safe_bool(getattr(model, "mixture_of_experts", False)),
        })

        self.llm = Llama(
            model_path=model.model,
            chat_format=chat_format,
            n_ctx=context,
            n_threads=threads,
            n_threads_batch=threads,
            n_batch=batch,
            n_ubatch=batch,
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
        self.stop_tokens = [
            s.strip() for s in (config.stop_tokens or "").split(",") if s.strip()
        ] or []

    def generate(self, prompt: str) -> str:
        logger.debug("📝 Generating response with llama.cpp")
        logger.debug({
            "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "stop_tokens": self.stop_tokens,
        })

        response = self.llm(
            prompt=prompt,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            top_p=self.top_p,
            stop=self.stop_tokens,
        )
        return response["choices"][0]["text"].strip()
