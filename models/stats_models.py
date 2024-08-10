from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class AgentsPickRates(Base):
    __tablename__ = "agents_pick_rates"

    index = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_id = Column(Integer, ForeignKey("stages.stage_id"))
    match_type_id = Column(Integer, ForeignKey("match_types.match_type_id"))
    map_id = Column(Integer, ForeignKey("maps.map_id"))
    agent_id = Column(Integer, ForeignKey("agents.agent"))
    pick_rate = Column(Float)
    year = Column(Integer)





