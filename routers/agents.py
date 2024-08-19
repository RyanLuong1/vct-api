from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.common_schemas import AgentBase
from models.common_models import Agents
from utility.db import get_db

router = APIRouter()

@router.get("/agents")
async def get_all_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agents))
    agents = jsonable_encoder(result.scalars().all())

    response = {item["agent"]: item["agent_id"] for item in agents if item["agent"]}
    return JSONResponse(content=response)

@router.get("/agents/{identifier}")
async def get_agent(identifier: str, db: AsyncSession = Depends(get_db)):
    if identifier.isdigit():
        result = await db.execute(select(Agents).where(Agents.agent_id == int(identifier)))
    else:
        result = await db.execute(select(Agents).where(Agents.agent == identifier))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"The agent was not found based on the id/name: {identifier}")
    agent = jsonable_encoder(result.scalars().first())
    response = {agent["agent"]: agent["agent_id"]}
    return JSONResponse(content=response)
