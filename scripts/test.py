import os
from llama_cpp import Llama

os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/bin/libllama.so"
MODEL_PATH = "/home/olmorera/AI/models/mixtral-8x7b-instruct-v0.1.Q5_K_M.gguf"

print(f"🔍 Using llama.cpp lib from: {os.environ['LLAMA_CPP_LIB']}")
print(f"📦 Loading model from: {MODEL_PATH}")

llm = Llama(
    model_path=MODEL_PATH,
    chat_format="mistral-instruct",
    mixture_of_experts=True,
    n_ctx=8192,
    n_threads=48,
    n_batch=64,
    use_mmap=True,
    use_mlock=False,
    numa=1,
    verbose=True
)

response = llm.create_chat_completion(messages=[
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is the capital of France?"}
])

print("🧠 Mixtral response:", response["choices"][0]["message"]["content"])
