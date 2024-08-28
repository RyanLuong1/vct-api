from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Agents
from utility.db import get_db
from utility.pools import agent_pool
import utility.common_values

router = APIRouter()

@router.get("/agents/pool")
async def get_agent_pool():
    
    response = agent_pool()
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

@router.get("/agents")
async def get_all_agents(db: AsyncSession = Depends(get_db)):
    response = utility.common_values.get_all_agents(db = db)
    return JSONResponse(content=response)
