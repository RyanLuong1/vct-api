from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func, case, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.stats_models import MapsStats, MapsScores
from utility.db import get_db
from utility.common_values import *

router = APIRouter()

@router.get("/maps-stats/trends/wr/team/{team_id}")
async def get_team_maps_win_loss_percentage_trends(team_id: int, db: AsyncSession = Depends(get_db)):
    team = get_team_by_id(team_id = team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")    

    maps = get_all_maps(db = db)
    response = {}

    win_sum = func.sum(
                    case(
                        (MapsScores.team_b_id == team_id, case((MapsScores.team_b_score > MapsScores.team_a_score, 1), else_=0)),else_=0)) + \
                func.sum(
                    case(
                        (MapsScores.team_a_id == team_id, case((MapsScores.team_a_score > MapsScores.team_b_score, 1), else_=0)), else_=0))

    total_maps_result = await db.execute(select(
        MapsScores.map_id,
        MapsScores.year,
        func.count().label("total_maps_played")
    ).where(
        and_(
            MapsScores.map_id != 0,
            or_(MapsScores.team_a_id == team_id,
                MapsScores.team_b_id == team_id))
    ).group_by(
        MapsScores.map_id,
        MapsScores.year
    ))

    total_wins_result = await db.execute(select(
        MapsScores.map_id,
        MapsScores.year,
        win_sum.label("total_wins")
    ).where(
        MapsScores.map_id != 0
    ).group_by(
        MapsScores.map_id,
        MapsScores.year
    ))

    total_maps_records = total_maps_result.all()
    total_wins_records = total_wins_result.all()

    total_maps_played = {}

    for record in total_maps_records:
        map, year, total_map = maps[record.map_id], record.year, record.total_maps_played
        year_dict = total_maps_played.setdefault(year, {})
        year_dict[map] = total_map
    total_wins = {}
    for record in total_wins_records:
        total_wins = record.total_wins
        if total_wins != 0:
            map, year = maps[record.map_id], record.year

            total_maps = total_maps_played[year][map]
            year_dict = response.setdefault(year, {})
            year_dict[map] = {"wr": round((total_wins / total_maps) * 100, 2),
                            "total_wins": total_wins,
                            "total_maps_played": total_maps}

    return JSONResponse(content=response)


@router.get("/maps-stats/wr/team/{team_id}")
async def get_team_maps_win_loss_percentage(team_id: int, db: AsyncSession = Depends(get_db)):
    team = get_team_by_id(team_id = team_id)

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")    

    maps = get_all_maps(db = db)
    response = {}

    win_sum = func.sum(
                    case(
                        (MapsScores.team_b_id == team_id, case((MapsScores.team_b_score > MapsScores.team_a_score, 1), else_=0)),else_=0)) + \
                func.sum(
                    case(
                        (MapsScores.team_a_id == team_id, case((MapsScores.team_a_score > MapsScores.team_b_score, 1), else_=0)), else_=0))

    total_maps_result = await db.execute(select(
        MapsScores.map_id,
        func.count().label("total_maps_played")
    ).where(
        and_(
            MapsScores.map_id != 0,
            or_(MapsScores.team_a_id == team_id,
                MapsScores.team_b_id == team_id))
    ).group_by(
        MapsScores.map_id
    ))

    total_wins_result = await db.execute(select(
        MapsScores.map_id,
        win_sum.label("total_wins")
    ).where(
        MapsScores.map_id != 0
    ).group_by(
        MapsScores.map_id
    ))


    total_maps_records = total_maps_result.all()
    total_wins_records = total_wins_result.all()

    total_maps_played = {record.map_id: record.total_maps_played for record in total_maps_records}

    for record in total_wins_records:
        map, total_wins, total_maps = maps[record.map_id], record.total_wins, total_maps_played[record.map_id]
        response[map] = {"wr": round((total_wins / total_maps) * 100, 2),
                         "total_wins": total_wins,
                         "total_maps_played": total_maps}

    return JSONResponse(content=response)


@router.get("/maps-stats/trends/wr")
async def get_maps_win_loss_percentage_trends(db: AsyncSession = Depends(get_db)):
    all_stages_ids = get_all_stages_ids(db = db)
    all_maps_id = get_all_maps_id(db = db)
    maps = get_all_maps(db = db)
    response = {}
    result = await db.execute(select(
        MapsStats.map_id,
        MapsStats.year,
        func.sum(MapsStats.total_maps_played).label("total_maps_played"),
        func.avg(MapsStats.attacker_side_win_percentage).label("overall_attk_wr"),
        func.avg(MapsStats.defender_side_win_percentage).label("overall_def_wr"),
    ).where(
        MapsStats.map_id != all_maps_id,
        MapsStats.map_id != 0,
        MapsStats.stage_id.in_(all_stages_ids)
    ).group_by(
        MapsStats.map_id,
        MapsStats.year
    )
    )

    for record in result:
        map, year, attk_wr, def_wr, total_maps_played = maps[record.map_id], record.year, jsonable_encoder(record.overall_attk_wr), jsonable_encoder(record.overall_def_wr), record.total_maps_played
        year_dict = response.setdefault(year, {})
        map_dict = year_dict.setdefault(map, {})
        map_dict["attk"] = round(attk_wr * 100, 2)
        map_dict["def"] = round(def_wr * 100, 2)
        map_dict["total_maps_played"] = total_maps_played
    return JSONResponse(content=response)

@router.get("/maps-stats/wr")
async def get_maps_win_loss_percentage(db: AsyncSession = Depends(get_db)):
    all_stages_ids = get_all_stages_ids(db = db)
    all_maps_id = get_all_maps_id(db = db)
    maps = get_all_maps(db = db)
    response = {}
    result = await db.execute(select(
        MapsStats.map_id,
        func.sum(MapsStats.total_maps_played).label("total_maps_played"),
        func.avg(MapsStats.attacker_side_win_percentage).label("overall_attk_wr"),
        func.avg(MapsStats.defender_side_win_percentage).label("overall_def_wr")
    ).where(
        MapsStats.map_id != all_maps_id,
        MapsStats.map_id != 0,
        MapsStats.stage_id.in_(all_stages_ids)
    ).group_by(
        MapsStats.map_id
    )
    )


    for record in result:
        map, attk_wr, def_wr, total_maps_played = maps[record.map_id], jsonable_encoder(record.overall_attk_wr), jsonable_encoder(record.overall_def_wr), record.total_maps_played
        map_dict = response.setdefault(map, {})
        map_dict["attk"] = round(attk_wr * 100, 2)
        map_dict["def"] = round(def_wr * 100, 2)
        map_dict["total_maps_played"] = total_maps_played
    return JSONResponse(content=response)
