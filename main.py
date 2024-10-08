from fastapi import FastAPI
from routers import agents, agents_pick_rates, tournaments, teams, players, maps, maps_stats, pick_bans, team_comp

app = FastAPI()

app.include_router(agents.router, prefix="")
app.include_router(tournaments.router, prefix="")
app.include_router(teams.router, prefix="")
app.include_router(players.router, prefix="")
app.include_router(maps.router, prefix="")
app.include_router(agents_pick_rates.router, prefix="")
app.include_router(maps_stats.router, prefix="")
app.include_router(pick_bans.router, prefix="")
app.include_router(team_comp.router, prefix="")