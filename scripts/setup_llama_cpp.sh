#!/bin/bash
set -euo pipefail

ENV_PATH=$(poetry env info --path 2>/dev/null)

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

echo "🔍 Verifying libllama.so at: $LIB_PATH"
if [[ ! -f "$LIB_PATH" ]]; then
  echo "❌ ERROR: libllama.so not found at $LIB_PATH"
  exit 1
fi

echo "🔍 Verifying presence of symbol: llama_kv_cache_view_init..."
if nm -D "$LIB_PATH" | grep 'llama_kv_cache_view_init' > /dev/null; then
  echo "✅ Symbol 'llama_kv_cache_view_init' found in libllama.so"
else
  echo "❌ ERROR: Symbol 'llama_kv_cache_view_init' NOT found in libllama.so"
  echo "💡 llama-cpp-python >= 0.3.9 will fail without this"
  exit 1
fi

# Export before install
export LLAMA_CPP_LIB="$LIB_PATH"

echo "📦 Optional: Reinstall llama-cpp-python from local source?"
read -rp "🔁 Reinstall llama-cpp-python now? [y/N]: " REPLY
if [[ "$REPLY" =~ ^[Yy]$ ]]; then
  pip uninstall -y llama-cpp-python || true
  pip install . --no-deps
  echo "✅ llama-cpp-python installed from local source."
fi

# Persist LLAMA_CPP_LIB in ~/.bashrc
if grep -q "^export LLAMA_CPP_LIB=" ~/.bashrc; then
  echo "🔁 Updating existing LLAMA_CPP_LIB in ~/.bashrc..."
  sed -i "s|^export LLAMA_CPP_LIB=.*|export LLAMA_CPP_LIB=\"$LIB_PATH\"|" ~/.bashrc
else
  echo "📍 Adding LLAMA_CPP_LIB to ~/.bashrc..."
  echo "export LLAMA_CPP_LIB=\"$LIB_PATH\"" >> ~/.bashrc
fi

if [[ -z "$ENV_PATH" ]]; then
  echo ""
  echo "⚠️  Poetry virtual environment not found."
  echo "   Please run the following first to create it:"
  echo ""
  echo "   poetry install"
  echo ""
  echo "🔁 Then, re-run this script or manually do:"
  echo "   source ~/.bashrc && source \$(poetry env info --path)/bin/activate"
  echo "   poetry run pip install /home/olmorera/AI/llama.cpp --no-deps"
  echo ""
else
  echo ""
  echo "🔄 To apply the environment and use llama-cpp-python, run:"
  echo ""
  echo "   source ~/.bashrc && source \"$ENV_PATH/bin/activate\""
  echo ""
  echo "📦 Then run inside the project:"
  echo ""
  echo "   poetry run pip uninstall -y llama-cpp-python || true"
  echo "   poetry run pip cache purge"
  echo "   poetry run pip install /home/olmorera/AI/llama.cpp --no-deps"
  echo ""
fi

echo "🎉 Done!"

