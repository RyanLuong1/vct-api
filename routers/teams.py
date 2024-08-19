from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.common_schemas import TeamBase
from models.common_models import Teams
from utility.db import get_db
from typing import Optional

router = APIRouter()

@router.get("/teams/search")
async def search_teams(name: Optional[str] = Query(None, min_length=1), db: AsyncSession = Depends(get_db)):
    if name:
        result = await db.execute(select(Teams).where(Teams.team.like(f"{name}%")))
        if not result:
            raise HTTPException(status_code=404, detail=f"The search was not able to find a list of teams similar to the name: {name}")
    else:
        result = await db.execute(select(Teams))
    teams = jsonable_encoder(result.scalars().all())
    response = {item["team"]: item["team_id"] for item in teams}
    return JSONResponse(content=response)

@router.get("/teams/{identifier}")
async def get_team(identifier: str, db: AsyncSession = Depends(get_db)):
    if identifier.isdigit():
        result = await db.execute(select(Teams).where(Teams.team_id == int(identifier)))
    else:
        result = await db.execute(select(Teams).where(Teams.team == identifier))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"The player was not found based on the id/name: {identifier}")
    teams = jsonable_encoder(result.scalars().all())
    response = {item["team"]: item["team_id"] for item in teams}
    return JSONResponse(content=response)

@router.get("/teams")
async def get_all_teams(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Teams))
    teams = jsonable_encoder(result.scalars().all())
    response = {item["team"]: item["team_id"] for item in teams}
    return JSONResponse(content=response)
