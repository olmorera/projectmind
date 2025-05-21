from scripts.reset_llm_models import reset_llm_models
from scripts.seed_prompts import seed_prompts

if __name__ == "__main__":
    print("🚀 Running full system seed (models + prompts)...")
    reset_llm_models()
    seed_prompts()
    print("🎉 Done seeding all components.")
