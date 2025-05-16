import os
import psutil
import time
from pathlib import Path
from llama_cpp import Llama

def get_model_name(path: str) -> str:
    return Path(path).stem.replace(".", "_")

def benchmark_model(model_path: str, prompt_path: str, output_dir: str = "outputs", max_tokens: int = 2048):
    os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/bin/libllama.so"
    logical_cores = round(psutil.cpu_count(logical=True) * 0.90)
    total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)

    # Optimal batch for 64GB or more
    batch_size = 64 if total_ram_gb >= 60 else 48 if total_ram_gb >= 40 else 32

    llm = Llama(
        model_path=model_path,
        chat_format="llama-2",
        n_ctx=16384,
        n_batch=batch_size,
        n_ubatch=batch_size,                 
        n_threads=logical_cores,
        n_threads_batch=logical_cores,
        #seed=-1,
        use_mmap=True,
        use_mlock=False,  
        numa=1,
        rope_scaling_type=2,  
        logits_all=False,
        embedding=False,
        offload_kqv=False,
        low_vram=False,
        f16_kv=False,
        verbose=True
    )


    with open(prompt_path, "r") as f:
        prompt = f.read()

    print(f"\n🚀 Benchmarking model: {Path(model_path).name}")
    print(f"🧪 Prompt: {Path(prompt_path).name} | Tokens: {max_tokens} | Batch: {batch_size}")

    start = time.time()
    response = llm(prompt, max_tokens=max_tokens)
    end = time.time()

    output_text = response["choices"][0]["text"]
    duration = end - start
    tokens_generated = response.get("usage", {}).get("completion_tokens", len(output_text.split()))
    speed = tokens_generated / duration if duration > 0 else 0

    print("\n===== GENERATED CODE =====\n")
    print(output_text)
    print("\n===== METRICS =====")
    print(f"🕒 Time: {duration:.2f} sec | 🧠 Tokens: {tokens_generated} | ⚡ Speed: {speed:.2f} tokens/sec")

    model_name = get_model_name(model_path)
    Path(output_dir).mkdir(exist_ok=True)
    output_file = Path(output_dir) / f"{model_name}.py"
    with open(output_file, "w") as f:
        f.write(output_text)

    print(f"\n✅ Code saved to: {output_file.resolve()}")

# Example usage:
if __name__ == "__main__":
    benchmark_model(
        model_path="/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
        prompt_path="scripts/benchmarks/prompts/module_prompt.txt"
    )
