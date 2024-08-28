from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select, distinct
from sqlalchemy.orm import aliased
from sqlalchemy.ext.asyncio import AsyncSession
from models.stats_models import AgentsPickRates, TeamsPickAgents, Overview
from models.junction_models import OverviewAgents
from utility.db import get_db
from utility.common_values import *

router = APIRouter()

@router.get("/pick-rates/agents/trends/team/{team_id}")
async def get_team_agents_pick_rates_trends(team_id: int, db: AsyncSession = Depends(get_db), include_maps:bool = Query(False), include_players: bool = Query(False)):
    team = get_team_by_id(db = db, team_id = team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")
    years = get_years(db = db, team_id = team_id)
    all_stages_ids = get_all_stages_ids(db = db, years = years)
    all_maps_id = get_all_maps_id(db = db)
    maps = get_all_maps(db = db)
    players = get_all_players(db = db)
    agents = get_all_agents(db = db)
    overview_agents = aliased(OverviewAgents)
    response = {}

    if include_players and include_maps:
        total_result = await db.execute(select(
                Overview.player_id,
                Overview.map_id,
                Overview.year,
                func.count().label("total_picks"),
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
            ).group_by(
                Overview.year,
                Overview.map_id,
                Overview.player_id
            ))    
        all_total_picks = total_result.all()
        total_picks = {}
        for record in all_total_picks:
            player, map, year, total_pick = players[record[0]], maps[record[1]], record[2], record[3]
            year_dict = total_picks.setdefault(year, {})
            map_dict = year_dict.setdefault(map, {})
            map_dict[player] = total_pick

        result = await db.execute(select(
                Overview.map_id,
                Overview.player_id,
                overview_agents.agent_id,
                Overview.year,
                func.count().label("total_agent_picks"),
            ).join(
                overview_agents,
                Overview.index == overview_agents.index
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.year.in_(years)
            ).group_by(
                Overview.year,
                Overview.map_id,
                overview_agents.agent_id,
                Overview.player_id
            ))    
        result = result.all()
        for record in result:
            map, player, agent, year, total_agent_pick = maps[record.map_id], players[record.player_id], agents[record.agent_id], record.year, record.total_agent_picks
            year_dict = response.setdefault(year, {})
            map_dict = year_dict.setdefault(map, {})
            player_dict = map_dict.setdefault(player, {})
            total_pick = total_picks[year][map][player]
            percentage = round((total_agent_pick / total_pick) * 100, 2)
            player_dict[agent] = jsonable_encoder(percentage)

    elif include_players:
        total_result = await db.execute(select(
                Overview.player_id,
                Overview.year,
                func.count().label("total_picks"),
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
            ).group_by(
                Overview.year,
                Overview.player_id
            ))    
        all_total_picks = total_result.all()
        total_picks = {}
        for record in all_total_picks:
            player, year, total_pick = players[record[0]], record[1], record[2]
            year_dict = total_picks.setdefault(year, {})
            year_dict[player] = total_pick
        result = await db.execute(select(
                Overview.player_id,
                overview_agents.agent_id,
                Overview.year,
                func.count().label("total_agent_picks"),
            ).join(
                overview_agents,
                Overview.index == overview_agents.index
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.year.in_(years)
            ).group_by(
                Overview.year,
                overview_agents.agent_id,
                Overview.player_id
            ))    
        result = result.all()
        for record in result:
            player, agent, year, total_agent_pick = players[record.player_id], agents[record.agent_id], record.year, record.total_agent_picks
            year_dict = response.setdefault(year, {})
            player_dict = year_dict.setdefault(player, {})
            total_pick = total_picks[year][player]
            percentage = round((total_agent_pick / total_pick) * 100, 2)
            player_dict[agent] = jsonable_encoder(percentage)

    elif include_maps:
        total_result = await db.execute(select(
                func.sum(TeamsPickAgents.total_maps_played).label("total_picks"),
                TeamsPickAgents.year,
                TeamsPickAgents.map_id
            ).where(
                TeamsPickAgents.stage_id.in_(all_stages_ids),
                TeamsPickAgents.team_id == team_id
            ).group_by(
                TeamsPickAgents.year,
                TeamsPickAgents.map_id
            ))    
        all_total_picks = total_result.all()
        total_picks = {}
        for record in all_total_picks:
            year_dict = total_picks.setdefault(record[1], {})
            year_dict[record[2]] = record[0]
        result = await db.execute(select(
            TeamsPickAgents.agent_id,
            TeamsPickAgents.map_id,
            TeamsPickAgents.year,
            func.sum(TeamsPickAgents.total_maps_played).label("total_agent_pick")
        ).where(
            TeamsPickAgents.stage_id.in_(all_stages_ids),
            TeamsPickAgents.team_id == team_id
        ).group_by(
            TeamsPickAgents.agent_id,
            TeamsPickAgents.map_id,
            TeamsPickAgents.year
        ))

        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            year = record.year
            total_pick = total_picks[year][record.map_id]
            map = maps[record.map_id]
            year_dict = response.setdefault(year, {})
            map_dict = year_dict.setdefault(map, {})
            percentage = round((record.total_agent_pick / total_pick) * 100, 2)
            map_dict[agent] = jsonable_encoder(percentage)
    else:
        total_result = await db.execute(select(
                func.sum(TeamsPickAgents.total_maps_played).label("total_picks"),
                TeamsPickAgents.year
            ).where(
                TeamsPickAgents.stage_id.in_(all_stages_ids),
                TeamsPickAgents.team_id == team_id
            ).group_by(
                TeamsPickAgents.year
            ))    
        all_total_picks = total_result.all()
        total_picks = {record[1]: record[0] for record in all_total_picks}
        result = await db.execute(select(
            TeamsPickAgents.agent_id,
            TeamsPickAgents.year,
            func.sum(TeamsPickAgents.total_maps_played).label("total_agent_pick")
        ).where(
            TeamsPickAgents.stage_id.in_(all_stages_ids),
            TeamsPickAgents.team_id == team_id
        ).group_by(
            TeamsPickAgents.agent_id,
            TeamsPickAgents.year
        ))
        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            year = record.year
            total_pick = total_picks[year]
            year_dict = response.setdefault(year, {})
            percentage = round((record.total_agent_pick / total_pick) * 100, 2)
            year_dict[agent] = jsonable_encoder(percentage)
    return JSONResponse(content = response)

@router.get("/pick-rates/agents/team/{team_id}")
async def get_team_agents_pick_rates(team_id: int, db: AsyncSession = Depends(get_db), include_maps: bool = Query(False), include_players: bool = Query(False)):
    team = get_team_by_id(db = db, team_id = team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")

    years = get_years(db = db, team_id = team_id)
    all_stages_ids = get_all_stages_ids(db = db, years = years)
    all_maps_id = get_all_maps_id(db = db)
    maps = get_all_maps(db = db)
    players = get_all_players(db = db)
    agents = get_all_agents(db = db)
    overview_agents = aliased(OverviewAgents)
    response = {}

    if include_maps and include_players:
        total_result = await db.execute(select(
                Overview.player_id,
                Overview.map_id,
                func.count().label("total_picks"),
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.map_id != 0
            ).group_by(
                Overview.map_id,
                Overview.player_id
            ))    
        all_total_picks = total_result.all()
        total_picks = {}
        for record in all_total_picks:
            player, map, total_pick = players[record[0]], maps[record[1]], record[2]
            map_dict = total_picks.setdefault(map, {})
            map_dict[player] = total_pick
        result = await db.execute(select(
                Overview.map_id,
                Overview.player_id,
                overview_agents.agent_id,
                func.count().label("total_agent_picks"),
            ).join(
                overview_agents,
                Overview.index == overview_agents.index
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.map_id != 0
            ).group_by(
                Overview.map_id,
                overview_agents.agent_id,
                Overview.player_id
            ))    
        result = result.all()
        for record in result:
            map, player, agent, total_agent_pick = maps[record.map_id], players[record.player_id], agents[record.agent_id], record.total_agent_picks
            map_dict = response.setdefault(map, {})
            player_dict = map_dict.setdefault(player, {})
            total_pick = total_picks[map][player]
            percentage = round((total_agent_pick / total_pick) * 100, 2)
            player_dict[agent] = jsonable_encoder(percentage)
    elif include_players:
        total_result = await db.execute(select(
                Overview.player_id,
                func.count().label("total_picks"),
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.map_id != 0
            ).group_by(
                Overview.player_id
            ))    
        all_total_picks = total_result.all()
        total_picks = {}
        for record in all_total_picks:
            player, total_pick = players[record[0]], record[1]
            total_picks[player] = total_pick
        result = await db.execute(select(
                Overview.player_id,
                overview_agents.agent_id,
                func.count().label("total_agent_picks"),
            ).join(
                overview_agents,
                Overview.index == overview_agents.index
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.map_id != 0
            ).group_by(
                overview_agents.agent_id,
                Overview.player_id
            ))    
        result = result.all()
        for record in result:
            player, agent, total_agent_pick = players[record.player_id], agents[record.agent_id], record.total_agent_picks
            player_dict = response.setdefault(player, {})
            total_pick = total_picks[player]
            percentage = round((total_agent_pick / total_pick) * 100, 2)
            player_dict[agent] = jsonable_encoder(percentage)
    elif include_maps:
        total_result = await db.execute(select(
                Overview.map_id,
                func.count().label("total_picks"),
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.map_id != 0
            ).group_by(
                Overview.map_id,
            ))    
        all_total_picks = total_result.all()
        total_picks = {}
        for record in all_total_picks:
            map, total_pick = maps[record[0]], record[1]
            total_picks[map] = total_pick
        result = await db.execute(select(
                Overview.map_id,
                overview_agents.agent_id,
                func.count().label("total_agent_picks"),
            ).join(
                overview_agents,
                Overview.index == overview_agents.index
            ).where(
                Overview.side == "both",
                Overview.team_id == team_id,
                Overview.map_id != all_maps_id,
                Overview.map_id != 0
            ).group_by(
                Overview.map_id,
                overview_agents.agent_id,
            ))    
        result = result.all()
        for record in result:
            map, agent, total_agent_pick = maps[record.map_id], agents[record.agent_id], record.total_agent_picks
            map_dict = response.setdefault(map, {})
            total_pick = total_picks[map]
            percentage = round((total_agent_pick / total_pick) * 100, 2)
            map_dict[agent] = jsonable_encoder(percentage)
    else:
        total_result = await db.execute(select(
            func.sum(TeamsPickAgents.total_maps_played)
        ).where(
            TeamsPickAgents.stage_id.in_(all_stages_ids)
        ))    
        total_picks = total_result.scalars().first()
        result = await db.execute(select(
            TeamsPickAgents.agent_id,
            func.sum(TeamsPickAgents.total_maps_played).label("total_agent_pick")
        ).where(
            TeamsPickAgents.stage_id.in_(all_stages_ids),
        ).group_by(
            TeamsPickAgents.agent_id,
        ))
        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            percentage = round((record.total_agent_pick / total_picks) * 100, 2)
            response[agent] = jsonable_encoder(percentage)
    return JSONResponse(content = response)

@router.get("/pick-rates/agents/trends")
async def get_agents_pick_rates_trends(db: AsyncSession = Depends(get_db), include_maps:bool = Query(False)):

    all_stages_ids = get_all_stages_ids(db = db)
    agents = get_all_agents(db = db)
    maps = get_all_maps(db = db)
    all_maps_id = get_all_maps_id(db = db)
    response = {}

    if include_maps:
        result = await db.execute(select(
            AgentsPickRates.agent_id,
            AgentsPickRates.map_id,
            AgentsPickRates.year,
            func.avg(AgentsPickRates.pick_rate).label("overall_pick_rate")
        ).where(
            AgentsPickRates.map_id.in_(maps),
            AgentsPickRates.stage_id.in_(all_stages_ids)
        ).group_by(
            AgentsPickRates.agent_id,
            AgentsPickRates.map_id,
            AgentsPickRates.year
        ))

        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            year = record.year
            map = maps[record.map_id]
            year_dict = response.setdefault(year, {})
            map_dict = year_dict.setdefault(map, {})
            percentage = round(record.overall_pick_rate * 100, 2)
            map_dict[agent] = jsonable_encoder(percentage)
    else:
        result = await db.execute(select(
            AgentsPickRates.agent_id,
            AgentsPickRates.year,
            func.avg(AgentsPickRates.pick_rate).label("overall_pick_rate")
        ).where(
            AgentsPickRates.map_id == all_maps_id,
            AgentsPickRates.stage_id.in_(all_stages_ids),
        ).group_by(
            AgentsPickRates.agent_id,
            AgentsPickRates.year
        ))

        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            year = record.year
            year_dict = response.setdefault(year, {})
            percentage = round(record.overall_pick_rate * 100, 2)
            year_dict[agent] = jsonable_encoder(percentage)
    return JSONResponse(content = response)


@router.get("/pick-rates/agents")
async def get_agents_pick_rates(db: AsyncSession = Depends(get_db), include_maps: bool = Query(False)):
    all_stages_ids = get_all_stages_ids(db = db)
    all_maps_id = get_all_maps_id(db = db)
    maps = get_all_maps(db = db)
    agents = get_all_agents(db = db)
    response = {}

    if include_maps:
        result = await db.execute(select(
            AgentsPickRates.agent_id,
            AgentsPickRates.map_id,
            func.avg(AgentsPickRates.pick_rate).label("overall_pick_rate")
        ).where(
            AgentsPickRates.map_id != all_maps_id,
            AgentsPickRates.map_id != 0,
            AgentsPickRates.stage_id.in_(all_stages_ids)
        ).group_by(
            AgentsPickRates.agent_id,
            AgentsPickRates.map_id
        ))

        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            map = maps[record.map_id]
            map_dict = response.setdefault(map, {})
            percentage = round(record.overall_pick_rate * 100, 2)
            map_dict[agent] = jsonable_encoder(percentage)

    else:
        result = await db.execute(select(
            AgentsPickRates.agent_id,
            func.avg(AgentsPickRates.pick_rate).label("overall_pick_rate")
        ).where(
            AgentsPickRates.map_id == all_maps_id,
            AgentsPickRates.stage_id.in_(all_stages_ids)
        ).group_by(
            AgentsPickRates.agent_id,
        ))

        result = result.all()
        for record in result:
            agent = agents[record.agent_id]
            percentage = round(record.overall_pick_rate * 100, 2)
            response[agent] = jsonable_encoder(percentage)
    return JSONResponse(content = response)