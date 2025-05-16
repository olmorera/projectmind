import os
import psutil
import time
from llama_cpp import Llama

# Force usage of the compiled llama.cpp lib
os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/bin/libllama.so"

# Auto-detect optimal values
physical_cores = psutil.cpu_count(logical=False)
logical_cores = psutil.cpu_count(logical=True)

# Set batch size based on available RAM
total_ram_gb = psutil.virtual_memory().total / (1024 ** 3)
batch_size = 48 if total_ram_gb >= 60 else 32

# Initialize LLM
llm = Llama(
    model_path="/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
    chat_format="llama-2",
    n_ctx=16384,
    n_batch=batch_size,
    n_ubatch=batch_size,
    n_threads=logical_cores,
    n_threads_batch=logical_cores,
    seed=42,
    use_mmap=True,
    use_mlock=True,
    numa=1,                   # 1 = distribute across NUMA nodes
    rope_scaling_type=1,      # 1 = linear
    logits_all=False,
    embedding=False,
    verbose=True
)

def test_realistic_code_generation():
    prompt = """
You are a senior software engineer. Generate a complete Python module named `file_processor.py` that contains:

- A class `FileProcessor` with methods:
  - `__init__(self, input_path: str)` to store the file path.
  - `read_file(self)` to read the contents of the file.
  - `count_words(self)` to return the number of words in the file.
  - `save_summary(self, output_path: str)` that saves a summary line like: "The file contains X words."
- Include full docstrings and error handling.
- Include a `main()` function that takes a file path as input from `sys.argv` and runs all steps.
"""

    start = time.time()
    response = llm(prompt, max_tokens=1024)
    end = time.time()

    print("\n===== GENERATED MODULE =====\n")
    print(response["choices"][0]["text"])
    print("\n===== TIMING =====")
    print(f"Elapsed time: {end - start:.2f} seconds")

if __name__ == "__main__":
    test_realistic_code_generation()
