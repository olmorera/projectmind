import os
os.environ["LLAMA_CPP_LIB"] = "/home/olmorera/AI/llama.cpp/build/bin/libllama.so"

from llama_cpp import Llama

llm = Llama(
    model_path="/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
    n_threads=48,
    n_batch=32,
    use_mlock=True,
    use_mmap=True,
    verbose=True
)

output = llm("def hello_world():", max_tokens=128)
print(output)
