from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Players
from utility.db import get_db
import utility.common_values
from typing import Optional
router = APIRouter()

@router.get("/players/search")
async def search_players(name: Optional[str] = Query(None, min_length=1), db: AsyncSession = Depends(get_db)):
    if name:
        result = await db.execute(select(Players).where(Players.player.like(f"{name}%")))
        if not result:
            raise HTTPException(status_code=404, detail=f"The search was not able to find a list of players similar to the name: {name}")
    else:
        players = await db.execute(select(Players))
    players = jsonable_encoder(result.scalars().all())
    response = {item["player"]: item["player_id"] for item in players}
    return JSONResponse(content=response)


@router.get("/players/{identifier}")
async def get_player(identifier: str, db: AsyncSession = Depends(get_db)):
    if identifier.isdigit():
        result = await db.execute(select(Players).where(Players.player_id == int(identifier)))
    else:
        result = await db.execute(select(Players).where(Players.player == identifier))
    
    if not result:
        raise HTTPException(status_code=404, detail=f"The player was not found based on the id/name: {identifier}")
    players = jsonable_encoder(result.scalars().all())
    response = {item["player"]: item["player_id"] for item in players}
    return JSONResponse(content=response)

@router.get("/players")
async def get_all_players(db: AsyncSession = Depends(get_db)):
    response = utility.common_values.get_all_players(db = db)
    return JSONResponse(content=response)

