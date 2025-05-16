import time
from projectmind.llm.llama_provider import LlamaProvider

MODEL_PATH = "/home/olmorera/AI/models/wizardcoder-python-34b-v1.0.Q5_K_M.gguf"
CONFIG = {
    "model_path": MODEL_PATH,
    "temperature": 0.1,
    "max_tokens": 1024,  # aumentamos para código real
    "top_p": 0.95,
    "n_threads": 48,
    "n_batch": 24
}

REAL_PROMPTS = [
    "Generate a login page using Flutter and Supabase",
    "Create a REST API in FastAPI with JWT authentication and role-based access",
    "Write a Svelte component with TailwindCSS that allows submitting a contact form and validates inputs",
    "Generate a Python script that scrapes product prices from an e-commerce site and stores them in PostgreSQL",
    "Generate a Flutter app with onboarding screens, login and dark mode support"
]

def run_prompt(prompt):
    print(f"\n🧪 Prompt: {prompt}")
    llm = LlamaProvider(CONFIG)

    start = time.perf_counter()
    output = llm.generate(prompt)
    end = time.perf_counter()

    lines = output.count("\n")
    duration = end - start

    print(f"⏱️ Time: {duration:.2f}s | 📄 Lines of code: {lines}")
    print(f"📦 Output Preview:\n{output[:300]}...\n")

if __name__ == "__main__":
    print(f"\n🚀 Real-world benchmark: WizardCoder 34B\n")
    for prompt in REAL_PROMPTS:
        run_prompt(prompt)
