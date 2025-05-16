# run_agent_test.py
from projectmind.agents.base_agent import AgentDefinition, BaseAgent
from projectmind.utils.logger import logger

agent_conf = AgentDefinition(
    name="Planner",
    role="Plans project structure",
    goal="Generate project plan from user input",
    type="planner"
)

agent = BaseAgent(agent_conf)
response = agent.run("Create a simple blog app")
print(response)
