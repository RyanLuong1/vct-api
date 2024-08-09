from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas.common_schemas import PlayerBase
from models.common_models import Players
from utility.db import get_db
from typing import Optional
router = APIRouter()

@router.get("/players/search", response_model=PlayerBase)
async def get_player(name: Optional[str] = Query(None, min_length=1), db: Session = Depends(get_db)):
    if name:
        players = jsonable_encoder(db.query(Players).filter(Players.player.like(f"{name}%")).all())
        if not players:
            raise HTTPException(status_code=404, detail=f"The search was not able to find a list of players similar to the name: {name}")
    else:
        players = jsonable_encoder(db.query(Players).all())
    response = {item["player"]: item["player_id"] for item in players}
    return JSONResponse(content=response)


@router.get("/players/{identifier}", response_model=PlayerBase)
async def get_player(identifier: str, db: Session = Depends(get_db)):
    if identifier.isdigit():
        player = db.query(Players).filter(Players.player_id == int(identifier)).first()
    else:
        player = db.query(Players).filter(Players.player == identifier).first()
    
    if not player:
        raise HTTPException(status_code=404, detail=f"The player was not found based on the id/name: {identifier}")
    response = jsonable_encoder(player)
    return JSONResponse(content=response)

@router.get("/players", response_model=PlayerBase)
async def get_all_players(db: Session = Depends(get_db)):
    players = jsonable_encoder(db.query(Players).all())
    response = {item["player"]: item["player_id"] for item in players}
    return JSONResponse(content=response)

