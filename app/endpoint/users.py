from pprint import pprint
from typing import Annotated
from redis import asyncio as redis
from fastapi import APIRouter, Depends, HTTPException, Response, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.core.redis_client import Redis
# from app.core.exception_handlers import CustomException
from app.core.security import get_hashed_psw, authenticate_user, create_access_token, create_refresh_token, decode_jwt
from app.db.CRUD import BaseCRUD
from app.schemas.user import SUserSignUp, SToken, STokenResponse, SOkResponse
from app.core.config import settings

users = APIRouter(
    prefix="/api/v1/users",
    tags=['users'],
)


@users.post('/auth/register', status_code=201)
async def registration(param: Annotated[SUserSignUp, Depends()], request: Request) -> SOkResponse:
    user = await get_hashed_psw(param, request.client.host)
    user_id = await BaseCRUD.add_user(user)
    return SOkResponse()


@users.post('/auth/login')
async def get_token(param: Annotated[OAuth2PasswordRequestForm, Depends()],
                    response: Response, request: Request) -> STokenResponse:
    user = await authenticate_user(username=param.username, password=param.password)
    # if request.client.host not in user.ip_list:
    #     send_email()
    payload = {'sub': user.user_id, 'role': user.role, 'username': user.username}
    access_token = create_access_token(data=payload)
    refresh_token = create_refresh_token(data=payload)
    response.set_cookie(key='access_token', value=access_token,
                        expires=60*settings.auth_jwt.access_token_expire_minutes)
    await Redis.set(request.client.host, refresh_token, 60*60*24*settings.auth_jwt.refresh_token_expire_days)
    return STokenResponse(data=SToken(access_token=access_token))


@users.post('/refresh')
async def auth_refresh_jwt(request: Request, response: Response) -> STokenResponse:

    payload = decode_jwt(token=await Redis.get(request.client.host))
    if payload.get('type') == 'access':
        raise HTTPException(
            status_code=403,
            detail='Incorrect refresh token'
        )

    refresh_token = create_refresh_token(data=payload)
    payload.update({'type': 'access'})
    access_token = create_access_token(data=payload)

    response.set_cookie(key='access_token', value=access_token)
    await Redis.set(request.client.host, refresh_token, 60*60*24*settings.auth_jwt.refresh_token_expire_days)
    return STokenResponse(data=SToken(access_token=access_token))


@users.post('/logout')
async def logout_user(response: Response, request: Request) -> SOkResponse:
    response.delete_cookie('access_token')
    await Redis.delete(request.client.host)
    return SOkResponse()

