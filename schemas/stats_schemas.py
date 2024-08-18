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

class TeamPickAgentBase(BaseModel):
    index: int
    tournament_id: int
    stage_id: int
    match_type_id: int
    map_id: int
    agent_id: int
    total_wins_by_map: int
    total_loss_by_map: int
    total_maps_played: int
    year: int

class OverviewBase(BaseModel):
    index: int
    tournament_id: int
    stage_id: int
    match_type_id: int
    match_id: int
    map_id: int
    player_id: int
    team_id: int
    rating: float
    acs: float
    kills: float
    deaths: float
    assists: float
    kd: float
    kast: float
    adpr: float
    headshot: float
    fk: float
    fd: float
    fkd: float
    side: str
    year: int