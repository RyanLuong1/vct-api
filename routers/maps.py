from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Maps
from utility.db import get_db
from utility.pools import map_pool
import utility.common_values
router = APIRouter()

@router.get("/maps/pool")
async def get_map_pool():
    response = map_pool()
    return JSONResponse(content=response)

@router.get("/maps/{identifier}")
async def get_map(identifier: str, db: AsyncSession = Depends(get_db)):
    if identifier.isdigit():
        result = await db.execute(select(Maps).where(Maps.map_id == int(identifier)))
    else:
        result = await db.execute(select(Maps).where(Maps.map == identifier))
    
    map = result.scalars().first()
    if not map:
        raise HTTPException(status_code=404, detail=f"The map was not found based on the id/name: {identifier}")
    response = {map.map: map.map_id}
    return JSONResponse(content=response)

@router.get("/maps")
async def get_all_maps(db: AsyncSession = Depends(get_db)):
    maps = await utility.common_values.get_all_maps(db = db)
    response = {map: map_id for map_id, map in maps.items()}
    return JSONResponse(content=response)