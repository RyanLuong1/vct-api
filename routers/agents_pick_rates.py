from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.stats_schemas import AgentPickRateBase
from models.stats_models import AgentsPickRates
from models.common_models import Agents, Maps, Stages
from utility.db import get_db
import asyncio

router = APIRouter()


@router.get("/pick-rates/agents", response_model=AgentPickRateBase)
async def get_all_agents(db: AsyncSession = Depends(get_db)):
    agents_result = await db.execute(select(Agents))
    maps_result = await db.execute(select(Maps))
    maps = jsonable_encoder(maps_result.scalars().all())
    agents = jsonable_encoder(agents_result.scalars().all())
    maps = {item["map_id"]: item["map"] for item in maps if item["map"]}
    agents = {item["agent_id"]: item["agent"] for item in agents if item["agent"]}
    response = {}
    result = await db.execute(select(
        AgentsPickRates.map_id,
        AgentsPickRates.agent_id,
        func.avg(AgentsPickRates.pick_rate).label("average_pick_rate")
    ).where(
        AgentsPickRates.map_id.in_(maps.keys()),
        AgentsPickRates.agent_id.in_(agents.keys())
    ).group_by(
        AgentsPickRates.year,
        AgentsPickRates.map_id,
        AgentsPickRates.agent_id
    ))

    result = result.all()
    for record in result:
        agent = agents[record.agent_id]
        map = maps[record.map_id]
        map_dict = response.setdefault(map, {})
        percentage = round(record.average_pick_rate * 100, 2)
        map_dict[agent] = jsonable_encoder(percentage)
    return JSONResponse(content = response)

