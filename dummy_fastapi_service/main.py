from fastapi import FastAPI
from .app.controllers.user_controller import router as user_router
from .app.controllers.team_controller import router as team_router

app = FastAPI(title="Dummy User Service")

app.include_router(user_router)
app.include_router(team_router)
