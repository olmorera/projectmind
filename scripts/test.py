from llama_cpp import Llama

llm = Llama(
    model_path="/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
    context_length=4096,
    n_threads=48,
    n_batch=64,
    max_tokens=2048,
    temperature=0.1,
    top_p=0.95
)

output = llm("Write a Python function to sum a list of integers.", max_tokens=512)
print(output["choices"][0]["text"])
