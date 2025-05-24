from projectmind.agents.agent_factory import AgentFactory


async def run_agent_once(agent_name: str, input: str, return_full_info: bool = False):
    agent = await AgentFactory.create(agent_name)
    response = await agent.arun(input)

    if return_full_info:
        return {
            "agent_name": agent.name,
            "input": input,
            "goal": agent.goal,
            "system_prompt": agent.definition.prompt,
            "response": response,
        }

    return response
