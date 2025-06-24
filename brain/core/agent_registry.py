from brain.agents.jalen_agent import JalenAgent
from brain.agents.sentinel_agent import SentinelAgent

class AgentRegistry:
    def __init__(self):
        self.agents = {}

    def register_agent(self, name, agent_class):
        self.agents[name] = agent_class()

    def get_agent(self, name):
        return self.agents.get(name)

    def list_agents(self):
        return list(self.agents.keys())
