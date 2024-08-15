from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.stats_schemas import AgentPickRateBase
from models.stats_models import AgentsPickRates
from models.common_models import Agents, Maps, Stages
from utility.db import get_db

router = APIRouter()


@router.get("/pick-rates/agents", response_model=AgentPickRateBase)
async def get_all_agents_pick_rates(db: AsyncSession = Depends(get_db)):
    stages_result = await db.execute(select(Stages.stage_id).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    maps_result = await db.execute(select(Maps.map_id).where(Maps.map == "All Maps"))
    all_maps_id = maps_result.scalars().first()
    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    response = {}
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

@router.get("/pick-rates/agents/trends", response_model=AgentPickRateBase)
async def get_all_agents_pick_rates_overtime(db: AsyncSession = Depends(get_db), include_maps:bool = Query(False)):

    stages_result = await db.execute(select(Stages.stage_id).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    agents_result = await db.execute(select(Agents))
    agents = agents_result.all()
    agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
    response = {}

    if include_maps:
        maps_result = await db.execute(select(Maps))
        all_maps = maps_result.all()
        maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
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
        maps_result = await db.execute(select(Maps.map_id).where(Maps.map == "All Maps"))
        all_maps_id = maps_result.scalars().first()
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

# @router.get("/pick-rates/agents/trends/maps", response_model=AgentPickRateBase)
# async def get_all_agents_pick_rates_overtime(db: AsyncSession = Depends(get_db)):
#     stages_result = await db.execute(select(Stages.stage_id).where(Stages.stage == "All Stages"))
#     all_stages_ids = stages_result.scalars().all()
#     maps_result = await db.execute(select(Maps))
#     all_maps = maps_result.all()
#     maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
#     agents_result = await db.execute(select(Agents))
#     agents = agents_result.all()
#     agents = {record[0].agent_id: record[0].agent for record in agents if record[0].agent}
#     response = {}
#     result = await db.execute(select(
#         AgentsPickRates.agent_id,
#         AgentsPickRates.map_id,
#         AgentsPickRates.year,
#         func.avg(AgentsPickRates.pick_rate).label("overall_pick_rate")
#     ).where(
#         AgentsPickRates.map_id.in_(maps),
#         AgentsPickRates.stage_id.in_(all_stages_ids)
#     ).group_by(
#         AgentsPickRates.agent_id,
#         AgentsPickRates.map_id,
#         AgentsPickRates.year
#     ))

#     result = result.all()
#     for record in result:
#         agent = agents[record.agent_id]
#         year = record.year
#         map = maps[record.map_id]
#         year_dict = response.setdefault(year, {})
#         map_dict = year_dict.setdefault(map, {})
#         percentage = round(record.overall_pick_rate * 100, 2)
#         map_dict[agent] = jsonable_encoder(percentage)
#     return JSONResponse(content = response)

