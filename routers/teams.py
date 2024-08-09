from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas.common_schemas import TeamBase
from models.common_models import Teams
from utility.db import get_db
from typing import Optional

router = APIRouter()

@router.get("/teams/search", response_model=TeamBase)
async def get_player(name: Optional[str] = Query(None, min_length=1), db: Session = Depends(get_db)):
    if name:
        teams = jsonable_encoder(db.query(Teams).filter(Teams.team.like(f"{name}%")).all())
        if not teams:
            raise HTTPException(status_code=404, detail=f"The search was not able to find a list of teams similar to the name: {name}")
    else:
        teams = jsonable_encoder(db.query(Teams).all())
    response = {item["team"]: item["team_id"] for item in teams}
    return JSONResponse(content=response)

@router.get("/teams/{identifier}", response_model=TeamBase)
async def get_agent(identifier: str, db: Session = Depends(get_db)):
    if identifier.isdigit():
        team = db.query(Teams).filter(Teams.team_id == int(identifier)).first()
    else:
        team = db.query(Teams).filter(Teams.team == identifier).first()
    
    if not team:
        raise HTTPException(status_code=404, detail=f"The team was not found based on the id/name: {identifier}")
    response = jsonable_encoder(team)
    return JSONResponse(content=response)

@router.get("/teams", response_model=TeamBase)
async def get_all_teams(db: Session = Depends(get_db)):
    agents = jsonable_encoder(db.query(Teams).all())
    response = {item["team"]: item["team_id"] for item in agents}
    return JSONResponse(content=response)
