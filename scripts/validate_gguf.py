# scripts/validate_gguf.py

import sys
import os
import ctypes
from llama_cpp import Llama
from loguru import logger


lib_dir = os.getenv("LLAMA_CPP_LIB_PATH")

# ✅ Establecer la ruta de la librería compilada
os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/bin/libllama.so"

ctypes.CDLL(os.path.join(lib_dir, "libllama.so"), mode=ctypes.RTLD_GLOBAL)

if len(sys.argv) < 2:
    print("Usage: poetry run python scripts/validate_gguf.py /path/to/model.gguf")
    sys.exit(1)

model_path = sys.argv[1]

if not os.path.isfile(model_path):
    print(f"❌ File does not exist: {model_path}")
    sys.exit(1)

logger.info(f"📦 Validating GGUF model: {model_path}")

try:
    # Paso 1: Cargar modelo con configuración básica
    llm = Llama(
        model_path=model_path,
        chat_format="chatml",
        n_ctx=2048,
        n_threads=os.cpu_count(),
        n_batch=32,
        numa=1,
        use_mmap=True,
        mixture_of_experts=True,  # For Mixtral safety
        verbose=True,
    )

    logger.success("✅ Model loaded successfully")

    # Paso 2: Validar generación
    prompt = "What is the capital of France?"
    logger.info(f"🧪 Generating test output for prompt: {prompt}")
    output = llm(prompt=prompt, max_tokens=32, temperature=0.7, stop=["</s>"])
    text = output["choices"][0]["text"].strip()

    logger.success(f"🧠 Model response: {text}")

except Exception as e:
    logger.error(f"❌ Model validation failed: {e}")
    sys.exit(1)
