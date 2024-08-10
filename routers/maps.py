from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas.common_schemas import MapBase
from models.common_models import Maps
from utility.db import get_db

router = APIRouter()

@router.get("/maps", response_model=MapBase)
async def get_all_agents(db: Session = Depends(get_db)):
    maps = jsonable_encoder(db.query(Maps).all())
    response = {item["map"]: item["map_id"] for item in maps if item["map"]}
    return JSONResponse(content=response)

@router.get("/maps/{identifier}", response_model=MapBase)
async def get_agent(identifier: str, db: Session = Depends(get_db)):
    if identifier.isdigit():
        map = db.query(Maps).filter(Maps.map_id == int(identifier)).first()
    else:
        map = db.query(Maps).filter(Maps.map == identifier).first()
    
    if not map:
        raise HTTPException(status_code=404, detail=f"The map was not found based on the id/name: {identifier}")
    response = jsonable_encoder(map)
    return JSONResponse(content=response)