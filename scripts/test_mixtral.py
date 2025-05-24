# scripts/test_mixtral.py
import os
from llama_cpp import Llama

# Asegúrate de que apunta a la lib personalizada
os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/libllama.so"

llm = Llama(
    model_path="/home/olmorera/AI/models/mixtral-8x7b-instruct-v0.1.Q5_K_M.gguf",
    chat_format="chatml",  # o "mistral-instruct" si da error
    n_ctx=8192,
    n_threads=32,         # ajusta según tus cores
    n_batch=64,
    use_mlock=False,
    use_mmap=True,
    numa=True,
    verbose=True
)

response = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain how Mixture of Experts works in Mixtral."}
    ]
)

print("🧠 Mixtral response:\n")
print(response["choices"][0]["message"]["content"])
