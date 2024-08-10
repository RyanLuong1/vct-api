from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class Agents(Base):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True)
    agent = Column(String)

class Maps(Base):
    __tablename__ = "maps"

    map_id = Column(Integer, primary_key=True)
    map = Column(String)

class Players(Base):
    __tablename__ = "players"

    player_id = Column(Integer, primary_key=True)
    player = Column(String)

class Teams(Base):
    __tablename__ = "teams"

    team_id = Column(Integer, primary_key=True)
    team = Column(String)

class Tournaments(Base):
    __tablename__ = "tournaments"

    tournament_id = Column(Integer, primary_key=True)
    tournament = Column(String)
    year = Column(Integer)

    stages = relationship("Stages", back_populates="tournaments")
    match_types = relationship("MatchTypes", back_populates="tournaments")

class Stages(Base):
    __tablename__ = "stages"

    stage_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_ = Column(String)
    year = Column(Integer)

    tournaments = relationship("Tournaments", back_populates="stages")
    match_types = relationship("MatchTypes", back_populates="stages")

class MatchTypes(Base):
    __tablename__ = "match_types"

    match_type_id = Column(Integer, primary_key=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.tournament_id"))
    stage_id = Column(Integer, ForeignKey("stages.stage_id"))
    match_type = Column(String)
    year = Column(Integer)

    tournaments = relationship("Tournaments", back_populates="match_types")
    stages = relationship("Stages", back_populates="match_types")