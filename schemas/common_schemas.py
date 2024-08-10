from pydantic import BaseModel
from typing import Optional

class AgentBase(BaseModel):
    agent_id:int
    agent: Optional[str] = None

class MapBase(BaseModel):
    map_id:int
    map_name: Optional[str] = None

class TeamBase(BaseModel):
    team_id:int
    team_name:str

class PlayerBase(BaseModel):
    player_id:int
    player_name:str

class TournamentBase(BaseModel):
    tournament_id:int
    tournament:str 
    year:int 

class StageBase(BaseModel):
    stage_id:int
    tournament_id:int
    stage:str 
    year:int 

class MatchTypeBase(BaseModel):
    match_type_id:int 
    tournament_id:int 
    stage_id:int 
    match_type:str 
    year:int 