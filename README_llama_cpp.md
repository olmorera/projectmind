# llama.cpp + llama-cpp-python Local Integration

This project uses a custom-compiled version of `llama.cpp` with support for `llama_kv_cache_view_init`, required by `llama-cpp-python >= 0.3.9`.

## 🛠 Setup Instructions

To build and install everything correctly, run:

```bash
./scripts/setup_llama_cpp.sh
```

This script will:

1. ✅ Clone the `abetlen/llama-cpp-python` repository (which includes `llama.cpp` as a submodule)
2. ✅ Checkout version `v0.3.9` (the last confirmed working version with `llama_kv_cache_view_init`)
3. ✅ Compile `llama.cpp` using CMake and your local CPU
4. ✅ Validate that the symbol `llama_kv_cache_view_init` is present in `libllama.so`
5. ✅ Set the `LLAMA_CPP_LIB` environment variable permanently in `~/.bashrc`
6. ✅ Optionally install `llama-cpp-python` globally

## 🧠 Activating the Environment

After running the setup script, apply the environment:

```bash
source ~/.bashrc && source "$(poetry env info --path)/bin/activate"
```

## 📦 Installing llama-cpp-python in Poetry

To ensure your Poetry environment uses the freshly built version:

```bash
poetry run pip uninstall -y llama-cpp-python || true
poetry run pip cache purge
poetry run pip install /home/olmorera/AI/llama.cpp --no-deps
```

## 🧪 Verify

To confirm everything is working, you can test inside the Poetry shell:

```bash
poetry run python
>>> from llama_cpp import Llama
>>> print("✅ llama-cpp-python is working.")
```

---

This ensures maximum compatibility and local performance with your GGUF models.
