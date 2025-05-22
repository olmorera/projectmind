#!/bin/bash
set -euo pipefail

LLAMA_DIR="/home/olmorera/AI/llama.cpp"
LIB_PATH="$LLAMA_DIR/build/bin/libllama.so"

echo "🧹 Removing previous llama.cpp build..."
rm -rf "$LLAMA_DIR"

echo "⬇️ Cloning llama-cpp-python with kv-cache compatible submodule..."
git clone --recurse-submodules https://github.com/abetlen/llama-cpp-python.git "$LLAMA_DIR"
cd "$LLAMA_DIR"

echo "📌 Checking out version compatible with llama_kv_cache_view_init..."
git checkout v0.3.9
git submodule update --init --recursive

echo "🧠 Configuring build with shared library and CPU optimizations..."
cmake -S . -B build \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_SHARED_LIBS=ON \
  -DLLAMA_BUILD_TESTS=OFF

echo "🚀 Compiling llama.cpp using $(nproc) cores..."
cmake --build build --config Release -j"$(nproc)"

echo "🔍 Verifying presence of symbol: llama_kv_cache_view_init..."
if nm -D "$LIB_PATH" | grep 'llama_kv_cache_view_init' > /dev/null; then
  echo "✅ Symbol 'llama_kv_cache_view_init' found in libllama.so"
else
  echo "❌ ERROR: Symbol 'llama_kv_cache_view_init' NOT found in libllama.so"
  echo "💡 llama-cpp-python >= 0.3.9 will fail without this"
  exit 1
fi

echo "📦 Optional: Reinstall llama-cpp-python from local source?"
read -rp "🔁 Reinstall llama-cpp-python now? [y/N]: " REPLY
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
  pip uninstall -y llama-cpp-python || true
  pip install . --no-deps
  echo "✅ llama-cpp-python installed from local source."
fi

# Optionally persist LLAMA_CPP_LIB for Python
if ! grep -q "LLAMA_CPP_LIB" ~/.bashrc; then
  echo "📍 Exporting LLAMA_CPP_LIB to ~/.bashrc..."
  echo "export LLAMA_CPP_LIB=\"$LIB_PATH\"" >> ~/.bashrc
  echo "✅ Added LLAMA_CPP_LIB to ~/.bashrc (restart shell to apply)"
fi

echo "🎉 Done! llama.cpp is compiled and ready at: $LIB_PATH"
