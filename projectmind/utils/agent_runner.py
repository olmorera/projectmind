from projectmind.agents.agent_factory import AgentFactory


async def run_agent_once(agent_name: str, user_prompt: str, return_full_info: bool = False):
    agent = await AgentFactory.create(agent_name)
    response = await agent.arun(input)

    if return_full_info:
        return {
            "agent_name": agent.name,
            "user_prompt": user_prompt,
            "goal": agent.goal,
            "system_prompt": agent.definition.system_prompt,
            "response": response,
        }

    return response
