from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, distinct, func, case, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession
from models.common_models import Maps, Stages, Teams
from models.stats_models import MapsStats, MapsScores, DraftPhase
from utility.db import get_db

router = APIRouter()


@router.get("/maps-stats/trends/picks-bans/team/{team_id}")
async def get_maps_win_loss_percentage(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")
    years_result = await db.execute(select(distinct(DraftPhase.year)).where(DraftPhase.team_id == team_id))
    years = years_result.scalars().all()  
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
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
@router.get("/maps-stats/trends/wr/team/{team_id}")
async def get_maps_win_loss_percentage(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")    

    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
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
async def get_maps_win_loss_percentage(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")    

    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
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
    total_wins = {}

    for record in total_wins_records:
        map, total_wins, total_maps = maps[record.map_id], record.total_wins, total_maps_played[record.map_id]
        response[map] = round((total_wins / total_maps) * 100, 2)

    return JSONResponse(content=response)

@router.get("/maps-stats/picks-bans/team/{team_id}")
async def get_maps_win_loss_percentage(team_id: int, db: AsyncSession = Depends(get_db)):
    team_result = await db.execute(select(Teams.team).where(Teams.team_id == team_id))
    team = team_result.scalars().first()

    if not team:
        raise HTTPException(status_code=404, detail=f"The team does not exist given the team id: {team_id}")    
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
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

@router.get("/maps-stats/trends/picks-bans")
async def get_maps_win_loss_percentage(db: AsyncSession = Depends(get_db)):
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    response = {}
    years = [2021, 2022, 2023, 2024]

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

@router.get("/maps-stats/trends/wr")
async def get_maps_win_loss_percentage(db: AsyncSession = Depends(get_db)):
    stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    maps_result = await db.execute(select(Maps.map_id).where(Maps.map == "All Maps"))
    all_maps_id = maps_result.scalars().first()
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    response = {}
    result = await db.execute(select(
        MapsStats.map_id,
        MapsStats.year,
        func.avg(MapsStats.attacker_side_win_percentage).label("overall_attk_wr"),
        func.avg(MapsStats.defender_side_win_percentage).label("overall_def_wr")
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
        map, year, attk_wr, def_wr = maps[record.map_id], record.year, jsonable_encoder(record.overall_attk_wr), jsonable_encoder(record.overall_def_wr)
        year_dict = response.setdefault(year, {})
        map_dict = year_dict.setdefault(map, {})
        map_dict["attk"] = round(attk_wr * 100, 2)
        map_dict["def"] = round(def_wr * 100, 2)
    return JSONResponse(content=response)

@router.get("/maps-stats/wr")
async def get_maps_win_loss_percentage(db: AsyncSession = Depends(get_db)):
    stages_result = await db.execute(select(distinct(Stages.stage_id)).where(Stages.stage == "All Stages"))
    all_stages_ids = stages_result.scalars().all()
    maps_result = await db.execute(select(Maps.map_id).where(Maps.map == "All Maps"))
    all_maps_id = maps_result.scalars().first()
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
    response = {}
    result = await db.execute(select(
        MapsStats.map_id,
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
        map, attk_wr, def_wr = maps[record.map_id], jsonable_encoder(record.overall_attk_wr), jsonable_encoder(record.overall_def_wr)
        map_dict = response.setdefault(map, {})
        map_dict["attk"] = round(attk_wr * 100, 2)
        map_dict["def"] = round(def_wr * 100, 2)
    return JSONResponse(content=response)

@router.get("/maps-stats/picks-bans")
async def get_maps_win_loss_percentage(db: AsyncSession = Depends(get_db)):
    maps_result = await db.execute(select(Maps))
    all_maps = maps_result.all()
    maps = {record[0].map_id: record[0].map for record in all_maps if record[0].map}
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