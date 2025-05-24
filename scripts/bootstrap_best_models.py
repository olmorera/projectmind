import asyncio
import uuid
from loguru import logger
from projectmind.db.session_async import AsyncSessionLocal
from projectmind.db.models import LLMModel, LLMConfig, Agent, Prompt

MODEL_CONFIGS = [
    {
        "name": "WizardCoder Python 34B",
        "model": "wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "chatml",
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
        "verbose": False,
        "rope_scaling_type": 2,
        "mixture_of_experts": False,
        "description": "Best for code review and technical analysis",
        "temperature": 0.3,
        "top_p": 1.0,
        "max_tokens": 1024,
        "stop_tokens": ["</s>"]
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
        "description": "Best for backend generation and Supabase logic",
        "temperature": 0.35,
        "top_p": 0.95,
        "max_tokens": 1024,
        "stop_tokens": ["</s>"]
    },
    {
        "name": "Zephyr 7B Beta",
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "zephyr",
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
        "description": "Excellent for planning, prompt optimization and evaluation",
        "temperature": 0.4,
        "top_p": 1.0,
        "max_tokens": 1024,
        "stop_tokens": ["</s>"]
    },
    {
        "name": "Mixtral 8x7B Instruct",
        "model": "Mixtral-8x7B-Instruct-v0.1.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "chatml",
        "n_ctx": 32768,
        "n_threads": 32,
        "n_batch": 64,
        "numa": 1,
        "f16_kv": True,
        "use_mlock": False,
        "use_mmap": True,
        "low_vram": False,
        "offload_kqv": False,
        "embedding": False,
        "logits_all": False,
        "verbose": False,
        "rope_scaling_type": None,
        "mixture_of_experts": True,
        "description": "Best for structured frontend UI code generation",
        "temperature": 0.3,
        "top_p": 0.95,
        "max_tokens": 1024,
        "stop_tokens": ["</s>"]
    },
    {
        "name": "Phi-2",
        "model": "phi-2.Q5_K_M.gguf",
        "provider": "llama",
        "chat_format": "chatml",
        "n_ctx": 2048,
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
        "description": "Fast and lightweight model ideal for simple evaluations and rating tasks",
        "temperature": 0.4,
        "top_p": 1.0,
        "max_tokens": 256,
        "stop_tokens": ["</s>"]
    }

]

AGENT_CONFIG = {
    "planner": {
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "type": "plan",
        "goal": "Break down high-level product ideas into detailed, actionable technical tasks.",
        "system_prompt": (
            "You are a professional technical planner.\n"
            "Your job is to transform user product ideas into a structured list of development tasks.\n"
            "Each task should be:\n"
            "- Actionable (clearly describes what to implement)\n"
            "- Ordered logically\n"
            "- Suitable for frontend/backend/infra agents\n"
            "- Avoid vague steps or unnecessary context\n\n"
            "Provide only the task list."
        ),
        "test_prompt": "Create an app that allows users to register, reset their password, and browse products."
    },
    "frontend_generator": {
        "model": "Mixtral-8x7B-Instruct-v0.1.Q5_K_M.gguf",
        "type": "frontend",
        "goal": "Generate responsive, well-structured UI using Svelte and TailwindCSS.",
        "system_prompt": (
            "You are a frontend engineer.\n"
            "Generate UI code using Svelte and TailwindCSS.\n"
            "Your output should be organized into files using headers like 'File: src/components/Login.svelte'.\n"
            "Avoid any explanations. Ensure accessibility and responsiveness."
        ),
        "test_prompt": "Generate a signup form with name, email, password, and submit button."
    },
    "backend_generator": {
        "model": "deepseek-coder-6.7b-instruct.Q5_K_M.gguf",
        "type": "backend",
        "goal": "Generate secure, scalable Supabase backend logic including SQL, RLS policies, and RPCs.",
        "system_prompt": (
            "You are a backend expert specialized in Supabase.\n"
            "Generate backend logic for the requested functionality including:\n"
            "- Database schema (PostgreSQL)\n"
            "- RLS policies\n"
            "- Supabase RPCs (via SQL functions)\n\n"
            "Group your output by file using 'File:' headers, and avoid any explanations."
        ),
        "test_prompt": "Build backend for a task manager with user-specific task lists, deadlines, and status updates."
    },
    "prompt_optimizer": {
        "model": "zephyr-7b-beta.Q5_K_M.gguf",
        "type": "optimize",
        "goal": "Rewrite prompts to be clearer, more focused, and technically robust.",
        "system_prompt": (
            "You are a senior prompt engineer.\n"
            "Improve the following prompt by making it clearer and more effective for a language model.\n"
            "Do not change its intent. Return only the improved version.\n\n"
            "PROMPT:\n{prompt}"
        ),
        "test_prompt": "Make this prompt better: Generate an HTML page with a navbar and two sections."
    },
    "code_reviewer": {
        "model": "wizardcoder-python-34b-v1.0.Q5_K_M.gguf",
        "type": "review",
        "goal": "Detect bugs, logic issues, and suggest concrete improvements to code.",
        "system_prompt": (
            "You are a senior code reviewer.\n"
            "Review the following Python code for correctness, efficiency, and best practices.\n"
            "Point out bugs or potential issues and suggest improvements using bullet points.\n\n"
            "CODE:\n{code}"
        ),
        "test_prompt": "Review this function: def is_even(n): return n % 2 == 1"
    },
    "prompt_evaluator": {
        "model": "phi-2.Q5_K_M.gguf",
        "type": "evaluate",
        "goal": "Rate how well an AI agent’s output satisfies its intended purpose, from 1 (poor) to 10 (perfect).",
        "system_prompt": (
            "You are an evaluator.\n"
            "Rate from 1 (terrible) to 10 (perfect) how well the AGENT RESPONSE fulfills the USER REQUEST.\n\n"
            "USER REQUEST:\n{user_prompt}\n\n"
            "AGENT RESPONSE:\n{response}\n\n"
            "⚠️ Respond ONLY with a single number between 1 and 10.\n"
            "❌ Do NOT explain. Do NOT repeat anything. Just return the number."
        ),
        "test_prompt": "RESPONSE: Hello! Let me know how I can help you today."
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
                stop_tokens=model["stop_tokens"],  # ✅ no serializado
                description=f"Base config for {model['model']}"
            )
            session.add(config)
            await session.flush()

            model_map[model["model"]] = (llm_model, config)

        for agent_name, cfg in AGENT_CONFIG.items():
            llm_model, llm_config = model_map[cfg["model"]]
            agent = Agent(
                id=str(uuid.uuid4()),
                name=agent_name,
                type=cfg["type"],
                goal=cfg["goal"],
                llm_config_id=llm_config.id,
                use_memory=True,
                can_create_tasks=(agent_name == "planner"),
                can_read_tasks=True,
                can_execute_tasks=True,
                optimize_prompt=(agent_name != "prompt_optimizer"),
                is_active=True,
                test_prompt=cfg.get("test_prompt")
            )
            session.add(agent)
            await session.flush()

            prompt = Prompt(
                id=str(uuid.uuid4()),
                agent_name=agent_name,
                task_type="default",
                system_prompt=cfg["system_prompt"],
                is_active=True,
                version="1.0",
                effectiveness_score=0.0
            )
            session.add(prompt)

        await session.commit()
        logger.success("✅ Bootstrap completed: models, configs, agents, and prompts initialized.")


if __name__ == "__main__":
    asyncio.run(bootstrap())
