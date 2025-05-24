import asyncio
import uuid
from projectmind.db.session_async import AsyncSessionLocal
from projectmind.db.models import LLMModel, LLMConfig, Agent, Prompt
from loguru import logger

# MODELS TO REGISTER WITH FULL CONFIGURATION
MODEL_CONFIGS = [
    {
        "name": "WizardCoder Python 34B",
        "model": "wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "llama-2",
        "n_ctx": 16384,
        "n_threads": 48,
        "n_batch": 64,
        "numa": 1,
        "f16_kv": False,
        "use_mlock": True,
        "use_mmap": True,
        "low_vram": False,
        "offload_kqv": False,
        "embedding": False,
        "logits_all": False,
        "verbose": True,
        "rope_scaling_type": 2,
        "mixture_of_experts": False,
        "description": "Best for frontend and structured code generation",
        "temperature": 0.3,
        "top_p": 1.0,
        "max_tokens": 1024,
        "stop_tokens": ""
    },
    {
        "name": "DeepSeek Coder 6.7B",
        "model": "deepseek-coder-6.7b-instruct.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "chatml",
        "n_ctx": 16384,
        "n_threads": 40,
        "n_batch": 64,
        "numa": 1,
        "f16_kv": False,
        "use_mlock": False,
        "use_mmap": True,
        "low_vram": False,
        "offload_kqv": False,
        "embedding": False,
        "logits_all": False,
        "verbose": False,
        "rope_scaling_type": 2,
        "mixture_of_experts": False,
        "description": "Strong for backend logic and Supabase integration",
        "temperature": 0.35,
        "top_p": 0.95,
        "max_tokens": 1024,
        "stop_tokens": ""
    },
    {
        "name": "Zephyr 7B Beta",
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "chatml",
        "n_ctx": 32768,
        "n_threads": 32,
        "n_batch": 64,
        "numa": 1,
        "f16_kv": False,
        "use_mlock": False,
        "use_mmap": True,
        "low_vram": False,
        "offload_kqv": False,
        "embedding": False,
        "logits_all": False,
        "verbose": False,
        "rope_scaling_type": 2,
        "mixture_of_experts": False,
        "description": "Fast and effective for planning and prompt optimization",
        "temperature": 0.4,
        "top_p": 1.0,
        "max_tokens": 1024,
        "stop_tokens": "</s>"
    },
    {
        "name": "OpenChat 3.5",
        "model": "openchat-3.5-0106.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "chatml",
        "n_ctx": 8192,
        "n_threads": 32,
        "n_batch": 64,
        "numa": 1,
        "f16_kv": False,
        "use_mlock": False,
        "use_mmap": True,
        "low_vram": False,
        "offload_kqv": False,
        "embedding": False,
        "logits_all": False,
        "verbose": False,
        "rope_scaling_type": 2,
        "mixture_of_experts": False,
        "description": "Conversational reasoning and fallback tasks",
        "temperature": 0.7,
        "top_p": 0.9,
        "max_tokens": 1024,
        "stop_tokens": "</s>"
    }
]

AGENT_CONFIG = {
    "planner": {
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "type": "plan",
        "goal": "Break down complex user goals into structured technical tasks.",
        "prompt": "You are a planning assistant. Break down the user's objective into clear, executable tasks for developers or AI agents. Each task should be specific, ordered, and technically feasible.",
        "test_input": "I want to build a website that includes user login, a contact form, and a blog section."
    },
    "frontend_generator": {
        "model": "wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
        "type": "frontend",
        "goal": "Generate structured and valid frontend UI code using Svelte and Tailwind.",
        "prompt": "You are a frontend expert. Generate clean Svelte components styled with TailwindCSS. Group code by file using 'File:' headers. Avoid explanations and ensure mobile responsiveness.",
        "test_input": "Create a login page with email and password using TailwindCSS."
    },
    "backend_generator": {
        "model": "deepseek-coder-6.7b-instruct.Q5_K_M.gguf",
        "type": "backend",
        "goal": "Generate secure Supabase backend logic and database structures.",
        "prompt": "You are a backend engineer. Generate Supabase-compatible backend logic including RPCs, SQL policies, and protected endpoints. Use clear naming and ensure user data safety.",
        "test_input": "Generate Supabase endpoints for managing blog posts and user data."
    },
    "prompt_optimizer": {
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "type": "optimize",
        "goal": "Improve prompt clarity, effectiveness, and structure without altering its meaning.",
        "prompt": "You are an expert in prompt optimization. Rewrite the following prompt to be clearer, more focused, and technically robust while preserving its intent. Return only the improved prompt.",
        "test_input": "Improve this prompt: Write a Python function to reverse a string."
    },
    "code_reviewer": {
        "model": "deepseek-coder-6.7b-instruct.Q5_K_M.gguf",
        "type": "review",
        "goal": "Review generated code and suggest improvements, detect bugs, or optimize structure.",
        "prompt": "You are a senior code reviewer. Analyze the following code snippet, detect logic errors, and suggest concrete improvements. Return your suggestions in bullet points.",
        "test_input": "Review this code: def sum(a, b): return a + b"
    },
    "prompt_evaluator": {
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "type": "evaluate",
        "goal": "Evaluate how well an AI response fulfills the agent's intended goal and return a score.",
        "prompt": (
            "You are an evaluator. Your job is to rate how well an AI agent's response fulfills the given goal.\n\n"
            "GOAL:\n{goal}\n\nRESPONSE:\n{response}\n\n"
            "Please answer with a single integer number from 1 (terrible) to 10 (perfect). Do not explain your answer."
        ),
        "test_input": "Rate this response: Hello world — for goal: greet the user."
    }
}

async def bootstrap():
    async with AsyncSessionLocal() as session:
        model_map = {}

        for model in MODEL_CONFIGS:
            llm_model = LLMModel(
                id=str(uuid.uuid4()),
                name=model["name"],
                model=f"/home/olmorera/AI/models/{model['model']}",
                provider=model["provider"],
                chat_format=model["chat_format"],
                n_ctx=model["n_ctx"],
                n_threads=model["n_threads"],
                n_batch=model["n_batch"],
                numa=model["numa"],
                f16_kv=model["f16_kv"],
                use_mlock=model["use_mlock"],
                use_mmap=model["use_mmap"],
                low_vram=model["low_vram"],
                offload_kqv=model["offload_kqv"],
                embedding=model["embedding"],
                logits_all=model["logits_all"],
                verbose=model["verbose"],
                rope_scaling_type=model["rope_scaling_type"],
                mixture_of_experts=model["mixture_of_experts"],
                description=model["description"]
            )
            session.add(llm_model)
            await session.flush()

            config = LLMConfig(
                id=str(uuid.uuid4()),
                name=f"Default config for {model['name']}",
                llm_model_id=llm_model.id,
                temperature=model["temperature"],
                top_p=model["top_p"],
                max_tokens=model["max_tokens"],
                stop_tokens=model["stop_tokens"],
                description=f"Base config for {model['model']}"
            )
            session.add(config)
            await session.flush()

            model_map[model["model"]] = (llm_model, config)

        for agent_name, config in AGENT_CONFIG.items():
            llm_model, llm_config = model_map[config["model"]]
            agent = Agent(
                id=str(uuid.uuid4()),
                name=agent_name,
                type=config["type"],
                goal=config["goal"],
                llm_config_id=llm_config.id,
                use_memory=True,
                can_create_tasks=(agent_name == "planner"),
                can_read_tasks=True,
                can_execute_tasks=True,
                optimize_prompt=(agent_name != "prompt_optimizer"),
                is_active=True,
                test_input=config.get("test_input")
            )
            session.add(agent)
            await session.flush()

            prompt = Prompt(
                id=str(uuid.uuid4()),
                agent_name=agent_name,
                task_type="default",
                prompt=config["prompt"],
                is_active=True,
                version="1.0",
                effectiveness_score=0.0
            )
            session.add(prompt)

        await session.commit()
        logger.success("✅ Bootstrap completed: models, configs, agents and prompts initialized.")

if __name__ == "__main__":
    asyncio.run(bootstrap())
