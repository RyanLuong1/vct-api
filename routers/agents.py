from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from schemas.common_schemas import AgentBase
from models.common_models import Agent
from utility.db import get_db

router = APIRouter()

@router.get("/agents", response_model=AgentBase)
async def get_all_agents(db: Session = Depends(get_db)):
    agents = jsonable_encoder(db.query(Agent).all())
    response = {item["agent"]: item["agent_id"] for item in agents}
    return JSONResponse(content=response)

@router.get("/agents/{identifier}", response_model=AgentBase)
async def get_agent(identifier: str, db: Session = Depends(get_db)):
    if identifier.isdigit():
        agent = db.query(Agent).filter(Agent.agent_id == int(identifier)).first()
    else:
        agent = db.query(Agent).filter(Agent.agent == identifier).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"The agent was not found based on the id/name: {identifier}")
    response = jsonable_encoder(agent)
    return JSONResponse(content=response)