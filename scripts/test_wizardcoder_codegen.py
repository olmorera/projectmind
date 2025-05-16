from llama_cpp import Llama
import time

# 📥 Prompt optimizado para obtener solo código útil
prompt = (
    "You are an expert Flutter developer. "
    "Generate only the Dart code for a login page using Flutter and Supabase. "
    "Include import statements and basic email/password authentication. "
    "Do not include explanations or extra text, only code between triple backticks.\n\n"
    "```dart\n"
)

# 🧠 Inicializar modelo con parámetros correctos
llm = Llama(
    model_path="/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
    chat_format="llama-2",
    n_ctx=16384,
    n_batch=64,
    n_ubatch=64,
    n_threads=48,
    n_threads_batch=48,
    seed=42,
    use_mmap=True,
    use_mlock=True,
    numa=1,                   # 1 = distribute
    rope_scaling_type=1,      # 1 = linear
    logits_all=False,
    embedding=False,
    verbose=True
)

# 🚀 Ejecutar y medir tiempo
start = time.time()
output = llm(
    prompt=prompt,
    max_tokens=1024,
    stop=["```"],
    echo=False,
)
end = time.time()

# 🖨️ Mostrar resultado
print(f"\n⏱️ Time: {end - start:.2f}s\n")
print("📦 Output:")
print(output["choices"][0]["text"].strip())
