# scripts/test_llm_speed.py

from projectmind.llm.llama_provider import LlamaProvider

llm = LlamaProvider({
    "model_path": "/home/olmorera/AI/models/zephyr-7b-beta.Q5_K_M.gguf",
    "temperature": 0.1,
    "max_tokens": 512,
    "top_p": 0.95,
    "n_threads": 48,
    "n_batch": 64,
})

prompt = "Write a Python function that takes a list of integers and returns the even numbers only."

output = llm.generate(prompt)
print("\n🧠 Output:\n", output)
