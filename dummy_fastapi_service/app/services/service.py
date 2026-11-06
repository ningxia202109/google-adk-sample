from typing import List, Optional
from ..models.schemas import User, UserCreate, UserUpdate, Team


class UserService:
    def __init__(self):
        self.users: List[User] = [
            User(
                id=1,
                name="Alice Smith",
                email="alice@example.com",
                habits=["swim", "read"],
            ),
            User(id=2, name="Bob Jones", email="bob@example.com", habits=["sing"]),
            User(
                id=3,
                name="Charlie Brown",
                email="charlie@example.com",
                habits=["football"],
            ),
        ]
        self.current_id = 4

    def get_users(self) -> List[User]:
        return self.users

    def get_user(self, user_id: int) -> Optional[User]:
        for user in self.users:
            if user.id == user_id:
                return user
        return None

    def create_user(self, user_create: UserCreate) -> User:
        new_user = User(
            id=self.current_id,
            name=user_create.name,
            email=user_create.email,
            habits=user_create.habits,
        )
        self.users.append(new_user)
        self.current_id += 1
        return new_user

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        for i, user in enumerate(self.users):
            if user.id == user_id:
                updated_data = user.model_dump()
                update_data = user_update.model_dump(exclude_unset=True)
                updated_data.update(update_data)
                updated_user = User(**updated_data)
                self.users[i] = updated_user
                return updated_user
        return None

    def delete_user(self, user_id: int) -> bool:
        for i, user in enumerate(self.users):
            if user.id == user_id:
                self.users.pop(i)
                return True
        return False


class TeamService:
    def __init__(self, user_service: UserService):
        self.teams: List[Team] = [
            Team(name="swim", members=[]),
            Team(name="read", members=[]),
            Team(name="football", members=[]),
            Team(name="sing", members=[]),
        ]
        self.user_service = user_service

    def get_teams(self) -> List[Team]:
        return self.teams

    def get_team(self, name: str) -> Optional[Team]:
        for team in self.teams:
            if team.name == name:
                return team
        return None

    def add_user_to_team(self, team_name: str, user_id: int) -> bool:
        team = self.get_team(team_name)
        if not team:
            return False

        user = self.user_service.get_user(user_id)
        if not user:
            return False

        # Check if habit matches team name
        if team_name not in (user.habits or []):
            return False

        if user_id not in team.members:
            team.members.append(user_id)
        return True

    def remove_user_from_team(self, team_name: str, user_id: int) -> bool:
        team = self.get_team(team_name)
        if not team:
            return False

        if user_id in team.members:
            team.members.remove(user_id)
            return True
        return False


user_service = UserService()
team_service = TeamService(user_service)
