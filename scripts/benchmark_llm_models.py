import time
from projectmind.llm.llama_provider import LlamaProvider

MODELS = [
    ("zephyr-7b-beta", "/home/olmorera/AI/models/zephyr-7b-beta.Q5_K_M.gguf"),
    ("deepseek-6.7b", "/home/olmorera/AI/models/deepseek-coder-6.7b-instruct.Q5_K_M.gguf"),
    ("phi-2", "/home/olmorera/AI/models/phi-2.Q4_K_M.gguf"),
]

prompt = "Write a Python function that takes a list of integers and returns only the even numbers."

def benchmark_model(name, path):
    print(f"\n🚀 Benchmarking {name}")
    llm = LlamaProvider({
        "model_path": path,
        "temperature": 0.1,
        "max_tokens": 512,
        "top_p": 0.95,
        "n_threads": 48,
        "n_batch": 64,
    })

    start = time.perf_counter()
    output = llm.generate(prompt)
    end = time.perf_counter()

    duration = end - start
    preview = output[:120].replace("\n", " ")
    print(f"⏱️ {duration:.2f} sec | 🧠 Output: {preview}...\n")

if __name__ == "__main__":
    for name, path in MODELS:
        benchmark_model(name, path)
