from fastapi import FastAPI
from routers import agents, agents_pick_rates, tournaments, teams, players, maps, maps_stats, pick_bans

app = FastAPI()

app.include_router(agents.router, prefix="/vct")
app.include_router(tournaments.router, prefix="/vct")
app.include_router(teams.router, prefix="/vct")
app.include_router(players.router, prefix="/vct")
app.include_router(maps.router, prefix="/vct")
app.include_router(agents_pick_rates.router, prefix="/vct")
app.include_router(maps_stats.router, prefix="/vct")
app.include_router(pick_bans.router, prefix="/vct")