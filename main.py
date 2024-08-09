from fastapi import FastAPI
from routers import agents, tournaments, teams, players

app = FastAPI()

app.include_router(agents.router, prefix="/vct")
app.include_router(tournaments.router, prefix="/vct")
app.include_router(teams.router, prefix="/vct")
app.include_router(players.router, prefix="/vct")