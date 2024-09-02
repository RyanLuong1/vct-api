from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, distinct
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Agents, Stages, Maps, Teams, Players, Tournaments
from models.stats_models import TeamsPickAgents

async def get_all_maps(db: AsyncSession):
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    return maps 


async def get_all_agents(db: AsyncSession):
    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    return agents

async def get_all_teams(db: AsyncSession):
    teams_result = await db.execute(select(Teams))
    teams = teams_result.all()
    teams = {record[0].team_id: record[0].team for record in teams if record[0].team}
    return teams

async def get_team_by_id(db: AsyncSession, team_id: int):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()
    return team

async def get_years(db: AsyncSession = None, team_id = None):
    if db and team_id:
        years_result = await db.execute(select(distinct(TeamsPickAgents.year)).where(TeamsPickAgents.team_id == team_id))
        years = years_result.scalars().all()
    else:
        years = [2021, 2022, 2023, 2024]
    return years

async def get_all_stages_ids(db: AsyncSession, years = None):
    if years:
        stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages", Stages.year.in_(years)))
    else:
        stages_result = await db.execute(select(Stages.stage_id).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    return all_stages_ids

async def get_all_maps_id(db: AsyncSession):
    maps_result = await db.execute(select(Maps.map_id).where(Maps.map == "All Maps"))
    all_maps_id = maps_result.scalars().first()
    return all_maps_id

async def get_all_players(db: AsyncSession):
    players_result = await db.execute(select(Players))
    all_players = players_result.all()
    players = {record[0].player_id: record[0].player for record in all_players if record[0].player}
    return players

async def get_all_tournaments(db: AsyncSession):
    result = await db.execute(select(Tournaments))
    tournaments = jsonable_encoder(result.scalars().all())
    response = {}
    for item in tournaments:
        year_dict = response.setdefault(item["year"], {})
        tournament, id = item["tournament"], item["tournament_id"]
        year_dict[id] = tournament
    return response
