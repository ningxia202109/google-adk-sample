from fastapi import APIRouter, HTTPException
from typing import List
from ..models.schemas import Team
from ..services.service import team_service

router = APIRouter(prefix="/teams", tags=["teams"])

@router.get("", response_model=List[Team])
def get_teams():
    return team_service.get_teams()

@router.post("/{team_name}/users/{user_id}", response_model=Team)
def add_user_to_team(team_name: str, user_id: int):
    success = team_service.add_user_to_team(team_name, user_id)
    if not success:
        raise HTTPException(
            status_code=400, 
            detail="Could not add user to team. Check if user exists and has matching habit."
        )
    return team_service.get_team(team_name)

@router.delete("/{team_name}/users/{user_id}", response_model=Team)
def remove_user_from_team(team_name: str, user_id: int):
    success = team_service.remove_user_from_team(team_name, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Team or user in team not found")
    return team_service.get_team(team_name)
