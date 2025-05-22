# projectmind/llm/llama_loader.py

import os
import ctypes
from loguru import logger

def load_llama_cpp_library():
    """Load the compiled llama.cpp shared library using LLAMA_CPP_LIB env variable."""
    lib_path = os.environ.get("LLAMA_CPP_LIB")

    if not lib_path or not os.path.isfile(lib_path):
        raise EnvironmentError(
            f"❌ LLAMA_CPP_LIB is not set correctly or the file does not exist.\n"
            f"Expected: {lib_path or 'not set'}\n\n"
            f"💡 Please set it before running:\n"
            f"export LLAMA_CPP_LIB=/home/olmorera/AI/llama.cpp/build/bin/libllama.so"
        )

    try:
        ctypes.CDLL(lib_path, mode=ctypes.RTLD_GLOBAL)
        logger.debug(f"✅ Loaded llama.cpp shared library from: {lib_path}")
    except OSError as e:
        raise RuntimeError(f"❌ Failed to load shared library: {e}")
