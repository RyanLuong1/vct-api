from sqlalchemy import Column, Integer, String, Float, ForeignKey, Interval
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


class TeamsPickAgents(Base):
    __tablename__ = "teams_picked_agents"

    index = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_id = Column(Integer, ForeignKey("stages.stage_id"))
    match_type_id = Column(Integer, ForeignKey("match_types.match_type_id"))
    team_id = Column(Integer, ForeignKey("teams.team_id"))
    map_id = Column(Integer, ForeignKey("maps.map_id"))
    agent_id = Column(Integer, ForeignKey("agents.agent"))
    total_wins_by_map = Column(Integer)
    total_loss_by_map = Column(Integer)
    total_maps_played = Column(Integer)
    year = Column(Integer)


class Overview(Base):
    __tablename__ = "overview"

    index = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_id = Column(Integer, ForeignKey("stages.stage_id"))
    match_type_id = Column(Integer, ForeignKey("match_types.match_type_id"))
    match_id = Column(Integer, ForeignKey("matches.match_id"))
    map_id = Column(Integer, ForeignKey("maps.map_id"))
    player_id = Column(Integer, ForeignKey("players.player_id"))
    team_id = Column(Integer, ForeignKey("teams.team_id"))
    rating = Column(Float)
    acs = Column(Float)
    kills = Column(Float)
    deaths = Column(Float)
    assists = Column(Float)
    kd = Column(Float)
    kast = Column(Float)
    adpr = Column(Float)
    headshot = Column(Float)
    fk = Column(Float)
    fd = Column(Float)
    fkd = Column(Float)
    side = Column(String)
    year = Column(Integer)

class MapsStats(Base):
    __tablename__ = "maps_stats"

    index = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_id = Column(Integer, ForeignKey("stages.stage_id"))
    match_type_id = Column(Integer, ForeignKey("match_types.match_type_id"))
    map_id = Column(Integer, ForeignKey("maps.map_id"))
    total_maps_played = Column(Integer)
    attacker_side_win_percentage = Column(Float)
    defender_side_win_percentage = Column(Float)
    year = Column(Integer)

class MapsScores(Base):
    __tablename__ = "maps_scores"
    index = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_id = Column(Integer, ForeignKey("stages.stage_id"))
    match_type_id = Column(Integer, ForeignKey("match_types.match_type_id"))
    match_id = Column(Integer, ForeignKey("matches.match_id"))
    map_id = Column(Integer, ForeignKey("maps.map_id"))
    team_a_id = Column(Integer, ForeignKey("teams.team_id"))
    team_b_id = Column(Integer, ForeignKey("teams.team_id"))
    team_a_score = Column(Integer)
    team_a_attacker_score = Column(Integer)
    team_a_defender_score = Column(Integer)
    team_a_overtime_score = Column(Integer)
    team_b_score = Column(Integer)
    team_b_attacker_score = Column(Integer)
    team_b_defender_score = Column(Integer)
    team_b_overtime_score = Column(Integer)
    duration = Column(Interval)
    year = Column(Integer)