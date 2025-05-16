import time
from projectmind.llm.llama_provider import LlamaProvider

MODEL_PATH = "/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf"
PROMPT = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
Generate a login page using Flutter and Supabase.

### Response:"""

MAX_TOKENS_VALUES = [512, 1024, 2048]
CTX_VALUES = [1024, 2048, 4096]
STOP_TOKENS_OPTIONS = [None, ["```"], ["```", "\n\n"]]
SUCCESS_KEYWORDS = ["def ", "class ", "import ", "function", "return", "<script", "const ", "final "]

def looks_like_code(output: str) -> bool:
    return any(keyword in output.lower() for keyword in SUCCESS_KEYWORDS)

def run_test(n_ctx, max_tokens, stop_tokens):
    config = {
        "model_path": MODEL_PATH,
        "temperature": 0.1,
        "max_tokens": max_tokens,
        "top_p": 0.95,
        "n_threads": 48,
        "n_batch": 64,
        "n_ctx": n_ctx,
    }

    print(f"\n🧪 Trying: n_ctx={n_ctx}, max_tokens={max_tokens}, stop={stop_tokens}")

    llm = LlamaProvider(config)
    # si tienes stop tokens en tu clase, modificalo dentro de generate()
    if stop_tokens:
        llm.llm.stop = stop_tokens

    start = time.perf_counter()
    output = llm.generate(PROMPT)
    end = time.perf_counter()

    duration = end - start
    print(f"⏱️ Time: {duration:.2f}s | ✂️ Preview:\n{output[:300]}...\n")

    if looks_like_code(output):
        print("✅ Output looks like real code. ✅\n")
        return True
    return False

if __name__ == "__main__":
    for n_ctx in CTX_VALUES:
        for max_tokens in MAX_TOKENS_VALUES:
            for stop_tokens in STOP_TOKENS_OPTIONS:
                success = run_test(n_ctx, max_tokens, stop_tokens)
                if success:
                    exit(0)

    print("❌ No configuration generated valid code.")
