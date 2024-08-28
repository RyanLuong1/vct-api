from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy import select, distinct, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Agents, Stages, Maps, Teams
from models.stats_models import TeamsPickAgents
from utility.db import get_db

router = APIRouter()


@router.get("/team-comp/trends/team/{team_id}")
async def get_specific_team_team_comp_trends(team_id: int,db: AsyncSession = Depends(get_db), limit: int = Query(10)):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")  
    
    elif limit <= 0:
        raise HTTPException(status_code=404, detail=f"The limit needs to be higher than 0. You provided {limit}")    

    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    response = {}
    result = await db.execute(
        select(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id,
            TeamsPickAgents.year,
            func.array_agg(TeamsPickAgents.agent_id).label("team_comp")
        ).where(
            TeamsPickAgents.stage_id.not_in(all_stages_ids),
            TeamsPickAgents.team_id == team_id
        ).group_by(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id,
            TeamsPickAgents.year
            )
    )

    team_comps = result.all()
    for record in team_comps:
        map = maps[record.map_id]
        year = record.year
        if len(record.team_comp) == 5:
            converted_agents = [agents[agent_id] for agent_id in record.team_comp]
            sorted_comp = sorted(converted_agents)
            team_comp = ", ".join(sorted_comp)
            year_dict = response.setdefault(year, {})
            map_dict = year_dict.setdefault(map, {})
            map_dict[team_comp] = map_dict.get(team_comp, 0) + 1

    for year, maps in response.items():
        for map, agent_comp_list in maps.items():
            top_n = sorted(agent_comp_list.items(), key=lambda x: x[1], reverse=True)[:limit]
            response[year][map] = {team_comp: count for team_comp, count in top_n}

    
    return JSONResponse(content = response)

@router.get("/team-comp/team/{team_id}")
async def get_specific_team_team_comp(team_id: int, db: AsyncSession = Depends(get_db), limit: int = Query(10)):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")   

    elif limit <= 0:
        raise HTTPException(status_code=404, detail=f"The limit needs to be higher than 0. You provided {limit}")    

    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    response = {}
    result = await db.execute(
        select(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id,
            func.array_agg(TeamsPickAgents.agent_id).label("team_comp")
        ).where(
            TeamsPickAgents.stage_id.not_in(all_stages_ids),
            TeamsPickAgents.team_id == team_id
        ).group_by(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id
            )
    )

    team_comps = result.all()
    for record in team_comps:
        map = maps[record.map_id]

        if len(record.team_comp) == 5:
            converted_agents = [agents[agent_id] for agent_id in record.team_comp]
            sorted_comp = sorted(converted_agents)
            team_comp = ", ".join(sorted_comp)
            map_dict = response.setdefault(map, {})
            map_dict[team_comp] = map_dict.get(team_comp, 0) + 1

    for map, agent_comp_list in response.items():
        top_n = sorted(agent_comp_list.items(), key=lambda x: x[1], reverse=True)[:limit]
        response[map] = {team_comp: count for team_comp, count in top_n}

    
    return JSONResponse(content = response)

@router.get("/team-comp/trends")
async def get_team_comp_per_year(db: AsyncSession = Depends(get_db), limit: int = Query(10)):
    if limit <= 0:
        raise HTTPException(status_code=404, detail=f"The limit needs to be higher than 0. You provided {limit}")    

    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    response = {}
    result = await db.execute(
        select(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id,
            TeamsPickAgents.year,
            func.array_agg(TeamsPickAgents.agent_id).label("team_comp")
        ).where(
            TeamsPickAgents.stage_id.not_in(all_stages_ids)
        ).group_by(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id,
            TeamsPickAgents.year
            )
    )

    team_comps = result.all()
    for record in team_comps:
        map = maps[record.map_id]
        year = record.year
        if len(record.team_comp) == 5:
            converted_agents = [agents[agent_id] for agent_id in record.team_comp]
            sorted_comp = sorted(converted_agents)
            team_comp = ", ".join(sorted_comp)
            year_dict = response.setdefault(year, {})
            map_dict = year_dict.setdefault(map, {})
            map_dict[team_comp] = map_dict.get(team_comp, 0) + 1

    for year, maps in response.items():
        for map, agent_comp_list in maps.items():
            top_n = sorted(agent_comp_list.items(), key=lambda x: x[1], reverse=True)[:limit]
            response[year][map] = {team_comp: count for team_comp, count in top_n}

    
    return JSONResponse(content = response)
@router.get("/team-comp")
async def get_team_comp(db: AsyncSession = Depends(get_db), limit: int = Query(10)):

    if limit <= 0:
        raise HTTPException(status_code=404, detail=f"The limit needs to be higher than 0. You provided {limit}")    

    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    response = {}
    result = await db.execute(
        select(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id,
            func.array_agg(TeamsPickAgents.agent_id).label("team_comp")
        ).where(
            TeamsPickAgents.stage_id.not_in(all_stages_ids)
        ).group_by(
            TeamsPickAgents.tournament_id,
            TeamsPickAgents.stage_id,
            TeamsPickAgents.match_type_id,
            TeamsPickAgents.map_id, 
            TeamsPickAgents.team_id
            )
    )

    team_comps = result.all()
    for record in team_comps:
        map = maps[record.map_id]

        if len(record.team_comp) == 5:
            converted_agents = [agents[agent_id] for agent_id in record.team_comp]
            sorted_comp = sorted(converted_agents)
            team_comp = ", ".join(sorted_comp)
            map_dict = response.setdefault(map, {})
            map_dict[team_comp] = map_dict.get(team_comp, 0) + 1

    for map, agent_comp_list in response.items():
        top_n = sorted(agent_comp_list.items(), key=lambda x: x[1], reverse=True)[:limit]
        response[map] = {team_comp: count for team_comp, count in top_n}

    
    return JSONResponse(content = response)
