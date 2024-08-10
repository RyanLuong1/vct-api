from pydantic import BaseModel
from typing import Optional

class AgentPickRateBase(BaseModel):
    index: int
    tournament_id: int 
    stage_id: int
    match_type_id: int 
    map_id: int
    agent_id: int
    pick_rate: float
    year: int