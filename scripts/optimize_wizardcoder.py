import time
from projectmind.llm.llama_provider import LlamaProvider

MODEL_PATH = "/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf"
prompt = "Write a complete Python script that reads a CSV file and outputs the average value of a numeric column."

batches = [16, 24, 32]
max_tokens_list = [256, 384, 512]

def benchmark(batch, max_tokens):
    print(f"🧪 batch={batch} | max_tokens={max_tokens} ", end="", flush=True)

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
    print(f"| ⏱️ {duration:.2f}s | ✂️ Output: {preview}...")

if __name__ == "__main__":
    print(f"\n🚀 Optimizing WIZARDCODER: {MODEL_PATH}\n")
    for batch in batches:
        for max_tokens in max_tokens_list:
            benchmark(batch, max_tokens)
