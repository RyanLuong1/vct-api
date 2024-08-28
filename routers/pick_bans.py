from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from models.stats_models import DraftPhase
from utility.db import get_db
from utility.common_values import *

router = APIRouter()


@router.get("/picks-bans/trends/team/{team_id}")
async def get_team_picks_bans_trends(team_id: int, db: AsyncSession = Depends(get_db)):
    team = get_team_by_id(db = db, team_id = team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")
    years = get_years(db = db, team_id = team_id)
    maps = get_all_maps(db = db)
    response = {}

    bans_result = await db.execute(select(
        DraftPhase.map_id,
        DraftPhase.year,
        func.count().label("total_bans_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban",
        DraftPhase.team_id == team_id
    ).group_by(
        DraftPhase.map_id,
        DraftPhase.year
    )
    )

    picks_result = await db.execute(select(
        DraftPhase.map_id,
        DraftPhase.year,
        func.count().label("total_picks_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick",
        DraftPhase.team_id == team_id
    ).group_by(
        DraftPhase.map_id,
        DraftPhase.year
    )
    )

    total_picks_result = await db.execute(select(
        DraftPhase.year,
        func.count().label("total_picks")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick",
        DraftPhase.team_id == team_id
    ).group_by(
        DraftPhase.year
    ))

    total_bans_result = await db.execute(select(
        DraftPhase.year,
        func.count().label("total_bans")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban",
        DraftPhase.team_id == team_id
    ).group_by(
        DraftPhase.year
    ))

    bans = {record.map_id: record.total_bans_per_map for record in bans_result.all()}
    picks = {record.map_id: record.total_picks_per_map for record in picks_result.all()}

    total_bans = {record.year: record.total_bans for record in total_bans_result.all()}
    total_picks = {record.year: record.total_picks for record in total_picks_result.all()}


    for year in years:
        year_dict = response.setdefault(year, {})
        total_global_bans = total_bans[year] 
        total_global_picks = total_picks[year]
        year_dict["total_global_bans"] = total_global_bans
        year_dict["total_global_picks"] = total_global_picks
        for id, map in maps.items():
            if map != "All Maps" and (id in bans and id in picks):
                bans_amt, picks_amt = bans[id], picks[id]
                year_dict = response.setdefault(year, {})
                year_dict[map] = {"pick_rate_map_specific": round((bans_amt / (bans_amt + picks_amt)) * 100, 2),
                                "ban_rate_map_specific": round((picks_amt / (bans_amt + picks_amt)) * 100, 2),
                                "pick_rate_global": round((picks_amt / total_global_bans) * 100, 2),
                                "ban_rate_global": round((bans_amt / total_global_picks) * 100, 2),
                                "total_picks": picks_amt,
                                "total_bans": bans_amt}
    return JSONResponse(content=response)

@router.get("/picks-bans/team/{team_id}")
async def get_team_picks_bans(team_id: int, db: AsyncSession = Depends(get_db)):
    team = get_team_by_id(db = db, team_id = team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")    
    maps = get_all_maps(db = db)
    response = {}

    bans_result = await db.execute(select(
        DraftPhase.map_id,
        func.count().label("total_bans_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban",
        DraftPhase.team_id == team_id
    ).group_by(
        DraftPhase.map_id
    )
    )

    picks_result = await db.execute(select(
        DraftPhase.map_id,
        func.count().label("total_picks_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick",
        DraftPhase.team_id == team_id
    ).group_by(
        DraftPhase.map_id
    )
    )

    total_picks_result = await db.execute(select(
        func.count().label("total_picks")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick",
        DraftPhase.team_id == team_id
    ))

    total_bans_result = await db.execute(select(
        func.count().label("total_bans")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban",
        DraftPhase.team_id == team_id
    ))

    bans = {record.map_id: record.total_bans_per_map for record in bans_result.all()}
    picks = {record.map_id: record.total_picks_per_map for record in picks_result.all()}

    total_bans = total_bans_result.scalars().first()
    total_picks = total_picks_result.scalars().first()
    response["total_global_bans"] = total_bans
    response["total_global_picks"] = total_picks
    for id, map in maps.items():
        if map != "All Maps" and (id in bans and id in picks):
            bans_amt, picks_amt = bans[id], picks[id]
            response[map] = {"pick_rate_map_specific": round((bans_amt / (bans_amt + picks_amt)) * 100, 2),
                            "ban_rate_map_specific": round((picks_amt / (bans_amt + picks_amt)) * 100, 2),
                            "pick_rate_global": round((picks_amt / total_bans) * 100, 2),
                            "ban_rate_global": round((bans_amt / total_picks) * 100, 2),
                            "total_picks": picks_amt,
                            "total_bans": bans_amt}
    return JSONResponse(content=response)

@router.get("/picks-bans/trends")
async def get_picks_bans_trends(db: AsyncSession = Depends(get_db)):
    maps = get_all_maps(db = db)
    response = {}
    years = get_years()

    bans_result = await db.execute(select(
        DraftPhase.map_id,
        DraftPhase.year,
        func.count().label("total_bans_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban"
    ).group_by(
        DraftPhase.map_id,
        DraftPhase.year
    )
    )

    picks_result = await db.execute(select(
        DraftPhase.map_id,
        DraftPhase.year,
        func.count().label("total_picks_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick"
    ).group_by(
        DraftPhase.map_id,
        DraftPhase.year
    )
    )

    total_picks_result = await db.execute(select(
        DraftPhase.year,
        func.count().label("total_picks")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick"
    ).group_by(
        DraftPhase.year
    ))

    total_bans_result = await db.execute(select(
        DraftPhase.year,
        func.count().label("total_bans")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban"
    ).group_by(
        DraftPhase.year
    ))

    bans = {record.map_id: record.total_bans_per_map for record in bans_result.all()}
    picks = {record.map_id: record.total_picks_per_map for record in picks_result.all()}

    total_bans = {record.year: record.total_bans for record in total_bans_result.all()}
    total_picks = {record.year: record.total_picks for record in total_picks_result.all()}


    for year in years:
        year_dict = response.setdefault(year, {})
        total_global_bans = total_bans[year] 
        total_global_picks = total_picks[year]
        year_dict["total_global_bans"] = total_global_bans
        year_dict["total_global_picks"] = total_global_picks
        for id, map in maps.items():
            if map != "All Maps":
                bans_amt, picks_amt = bans[id], picks[id]
                year_dict = response.setdefault(year, {})
                year_dict[map] = {"pick_rate_map_specific": round((bans_amt / (bans_amt + picks_amt)) * 100, 2),
                                "ban_rate_map_specific": round((picks_amt / (bans_amt + picks_amt)) * 100, 2),
                                "pick_rate_global": round((picks_amt / total_global_bans) * 100, 2),
                                "ban_rate_global": round((bans_amt / total_global_picks) * 100, 2),
                                "total_picks": picks_amt,
                                "total_bans": bans_amt}
    return JSONResponse(content=response)

@router.get("/picks-bans")
async def get_picks_bans(db: AsyncSession = Depends(get_db)):
    maps = get_all_maps(db = db)
    response = {}

    bans_result = await db.execute(select(
        DraftPhase.map_id,
        func.count().label("total_bans_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban"
    ).group_by(
        DraftPhase.map_id
    )
    )

    picks_result = await db.execute(select(
        DraftPhase.map_id,
        func.count().label("total_picks_per_map") 
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick"
    ).group_by(
        DraftPhase.map_id
    )
    )

    total_picks_result = await db.execute(select(
        func.count().label("total_picks")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "pick"
    ))

    total_bans_result = await db.execute(select(
        func.count().label("total_bans")
    ).where(
        DraftPhase.map_id != 0,
        DraftPhase.action == "ban"
    ))

    bans = {record.map_id: record.total_bans_per_map for record in bans_result.all()}
    picks = {record.map_id: record.total_picks_per_map for record in picks_result.all()}

    total_bans = total_bans_result.scalars().first()
    total_picks = total_picks_result.scalars().first()
    response["total_global_bans"] = total_bans
    response["total_global_picks"] = total_picks
    for id, map in maps.items():
        if map != "All Maps":
            bans_amt, picks_amt = bans[id], picks[id]
            response[map] = {"pick_rate_map_specific": round((bans_amt / (bans_amt + picks_amt)) * 100, 2),
                            "ban_rate_map_specific": round((picks_amt / (bans_amt + picks_amt)) * 100, 2),
                            "pick_rate_global": round((picks_amt / total_bans) * 100, 2),
                            "ban_rate_global": round((bans_amt / total_picks) * 100, 2),
                            "total_picks": picks_amt,
                            "total_bans": bans_amt}
    return JSONResponse(content=response)