from llama_cpp import Llama

llm = Llama(
    model_path="/home/olmorera/AI/models/mixtral-8x7b-instruct-v0.1.Q4_K_M.gguf",
    n_ctx=8192,
    n_threads=32,
    n_batch=64,
    use_mmap=True,
    use_mlock=False,
    numa=True,
    f16_kv=True,
    rope_freq_base=500000,
    chat_format="chatml",  # IMPORTANTE: Mixtral usa chatml
    verbose=True
)

for k, v in llm.metadata.items():
    print(f"{k}: {v}")

output = llm.create_chat_completion(
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is the capital of France?"}
    ],
    temperature=0.3,
    top_p=0.95,
    max_tokens=100
)

print(output["choices"][0]["message"]["content"])
