import argparse
import os
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from fastapi import FastAPI, Depends
from starlette.middleware.sessions import SessionMiddleware

from app.libs.config import Config
from app.model import User
from app.routers import auth
from app.routers.auth import get_current_user

config = Config()
app = FastAPI()
app.include_router(auth.router)
app.add_middleware(SessionMiddleware, secret_key=config.get_session_secret_key())


@app.get("/")
async def home(user: Optional[User] = Depends(get_current_user)):
    if user:
        return {'status': 'login', 'user': user}
    else:
        return {'status': 'logout'}

