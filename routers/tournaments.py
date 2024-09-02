from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Tournaments
from utility.db import get_db
from utility.pools import tournament_pool
import utility.common_values
from typing import Optional

router = APIRouter()

@router.get("/tournaments/pool")
async def get_tournament_pool():
    response = tournament_pool()
    return JSONResponse(content = response)

# @router.get("/tournaments/search")
# async def search_tournaments(name: Optional[str] = Query(None, min_length=1), db: AsyncSession = Depends(get_db)):
#     print(name)
#     if name:
#         result = await db.execute(select(Tournaments).where(Tournaments.tournament.like(f"{name}%")))
#         if not result:
#             raise HTTPException(status_code=404, detail=f"The search was not able to find a list of tournaments similar to the name: {name}")
#     else:
#         result = await db.execute(select(Tournaments))
#     tournaments = jsonable_encoder(result.scalars().all())
#     response = {}
#     for item in tournaments:
#         year_dict = response.setdefault(item["year"], {})
#         tournament, id = item["tournament"], item["tournament_id"]
#         year_dict[tournament] = id
#     return JSONResponse(content=response)

@router.get("/tournaments/year/{year}")
async def get_tournament_based_on_year(year: str, db: AsyncSession = Depends(get_db)):
    if year.isdigit():
        if 2021 <= int(year) <= 2024:
            result = await db.execute(select(Tournaments).where(Tournaments.year == int(year)))
            response = {}
            tournaments = jsonable_encoder(result.scalars().all())
            for item in tournaments:
                tournament, id = item["tournament"], item["tournament_id"]
                response[tournament] = id
            return JSONResponse(content=response)
        else:
            raise HTTPException(status_code=404, detail=f"You provided a year that is not within VCT: {year}")

    else:
        raise HTTPException(status_code=404, detail=f"You did not provide a year!")

@router.get("/tournaments")
async def get_all_tournaments(db: AsyncSession = Depends(get_db)):
    tournaments = await utility.common_values.get_all_tournaments(db = db)
    response = {}
    for year, tournament_list in tournaments.items():
        year_dict = response.setdefault(year, {})
        for tournament_id, tournament in tournament_list.items():
            year_dict[tournament] = tournament_id
    return JSONResponse(content=response)
