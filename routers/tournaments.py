from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas.common_schemas import TournamentBase
from models.common_models import Tournaments
from utility.db import get_db
from typing import Optional

router = APIRouter()

@router.get("/tournaments/search", response_model=TournamentBase)
async def get_player(name: Optional[str] = Query(None, min_length=1), db: Session = Depends(get_db)):
    if name:
        tournaments = jsonable_encoder(db.query(Tournaments).filter(Tournaments.tournament.like(f"{name}%")).all())
        if not tournaments:
            raise HTTPException(status_code=404, detail=f"The search was not able to find a list of tournaments similar to the name: {name}")
    else:
        tournaments = jsonable_encoder(db.query(Tournaments).all())
    response = {}
    for item in tournaments:
        year_dict = response.setdefault(item["year"], {})
        tournament, id = item["tournament"], item["tournament_id"]
        year_dict[tournament] = id
    return JSONResponse(content=response)

@router.get("/tournaments/year/{year}", response_model=TournamentBase)
async def get_tournament_based_on_year(year: str, db: Session = Depends(get_db)):
    if year.isdigit():
        tournaments = jsonable_encoder(db.query(Tournaments).filter(Tournaments.year == int(year)).all())
        response = {}
        for item in tournaments:
            tournament, id = item["tournament"], item["tournament_id"]
            response[tournament] = id
        return JSONResponse(content=response)

    else:
        raise HTTPException(status_code=404, detail=f"You did not provide a year!")

@router.get("/tournaments", response_model=TournamentBase)
async def get_all_tournaments(db: Session = Depends(get_db)):
    tournaments = jsonable_encoder(db.query(Tournaments).all())
    response = {}
    for item in tournaments:
        year_dict = response.setdefault(item["year"], {})
        tournament, id = item["tournament"], item["tournament_id"]
        year_dict[tournament] = id
    return JSONResponse(content=response)