import time
from typing import Optional

import aiohttp as aiohttp
from authlib.integrations.starlette_client import OAuth
from authlib.oauth2.rfc6749 import OAuth2Token
from fastapi import Depends, APIRouter
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.libs.config import Config
from app.model import User


SESSION_USER_KEY = 'user'

router = APIRouter()

config = Config()
oauth = OAuth()
oauth.register(
    name='discord',
    client_id=config.get_client_id(),
    client_secret=config.get_client_secret(),
    authorize_url='https://discordapp.com/api/oauth2/authorize',
    access_token_url='https://discordapp.com/api/oauth2/token',
    client_kwargs={'scope': ' '.join(['identify', 'guilds', 'email'])},
)


def get_current_user(request: Request) -> Optional[User]:
    if SESSION_USER_KEY not in request.session:
        return
    kwargs = request.session[SESSION_USER_KEY]
    if time.time() >= kwargs.get('expires_at', 0):
        return

    try:
        return User(**kwargs)
    except:
        return


@router.get("/login")
async def login_via_discord(request: Request, user: Optional[User] = Depends(get_current_user)):
    if user:
        return RedirectResponse(url='/')
    redirect_uri = request.url_for('auth_via_discord')
    return await oauth.discord.authorize_redirect(request, redirect_uri)


@router.get("/auth/discord")
async def auth_via_discord(request: Request):
    token_response: OAuth2Token = await oauth.discord.authorize_access_token(request)
    access_token = token_response['access_token']
    async with aiohttp.ClientSession() as sess:
        r = await sess.get('https://discordapp.com/api/users/@me', headers={'Authorization': f'Bearer {access_token}'})
        if not 200 <= r.status < 300:
            return RedirectResponse(url='/')
        res_me = await r.json()

    token_response['id'] = res_me['id']
    token_response['name'] = res_me['username']
    request.session[SESSION_USER_KEY] = token_response
    return RedirectResponse(url='/')


@router.get("/logout")
async def logout(request: Request, user: Optional[User] = Depends(get_current_user)):
    if user:
        request.session.pop(SESSION_USER_KEY)
    return RedirectResponse(url='/')
