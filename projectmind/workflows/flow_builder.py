import os
from dotenv import load_dotenv
from langgraph.graph import StateGraph
from langgraph.checkpoint.postgres import PostgresSaver
from langchain_core.runnables import RunnableLambda

from projectmind.workflows.agent_executor import agent_node

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

with PostgresSaver.from_conn_string(DATABASE_URL) as saver:
    saver.setup()
    checkpointer = saver


def agent_flow():
    workflow = StateGraph(dict)
    workflow.add_node("agent", RunnableLambda(agent_node))

    def router(state):
        return "agent"

    workflow.set_conditional_entry_point(router)
    workflow.set_finish_point("agent")
    return workflow.compile().with_config({"checkpointer": checkpointer})
