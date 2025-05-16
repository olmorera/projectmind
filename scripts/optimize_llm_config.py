import time
from projectmind.llm.llama_provider import LlamaProvider

MODEL_PATH = "/home/olmorera/AI/models/deepseek-coder-6.7b-instruct.Q5_K_M.gguf"
prompt = "Write a Python function that takes a list of integers and returns only the even numbers."

# Variaciones de parámetros
batch_sizes = [32, 48, 64, 80]
max_tokens_list = [256, 384, 512, 640]

def benchmark(batch, max_tokens):
    llm = LlamaProvider({
        "model_path": MODEL_PATH,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "top_p": 0.95,
        "n_threads": 48,
        "n_batch": batch,
    })

    start = time.perf_counter()
    output = llm.generate(prompt)
    end = time.perf_counter()

    duration = end - start
    preview = output[:80].replace("\n", " ")
    print(f"🧪 batch={batch:<3} | max_tokens={max_tokens:<3} | ⏱️ {duration:.2f}s | ✂️ Output: {preview}...")

if __name__ == "__main__":
    print(f"\n🚀 Optimizing LLM Config: {MODEL_PATH}\n")
    for batch in batch_sizes:
        for max_tokens in max_tokens_list:
            benchmark(batch, max_tokens)
