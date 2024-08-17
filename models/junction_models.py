from sqlalchemy import Column, Integer, ForeignKey
from database import Base

class AgentsPickRates(Base):
    __tablename__ = "overview_agents"

    id = Column(Integer, primary_key=True)
    index = Column(Integer, ForeignKey("overview.index"))
    agent_id = Column(Integer, ForeignKey("agents.agent_id"))
    year = Column(Integer)