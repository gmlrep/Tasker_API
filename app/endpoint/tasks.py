from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, WebSocket, WebSocketDisconnect

from app.core.security import is_refresh_token, valid_cookies, decode_jwt, is_valid_token
from app.db.database import ClientDB
from app.schemas.task import STask, SUserTask
from app.schemas.user import SIsOk

tasks = APIRouter(
    prefix="/api/v1/tasks",
    tags=['tasks'],
    dependencies=[Depends(valid_cookies)]
)


# async def get_task_list(websocket: WebSocket, user_id: int):
#     tasks_shared = await ClientDB.get_tasks(user_id=user_id, is_shared=True)
#     for task in tasks_shared:
#         print(task)
#         await websocket.send_text(str(task))

# websocket_clients = []


@tasks.post('/', status_code=201, dependencies=[Depends(valid_cookies)])
async def create_task(param: Annotated[STask, Depends()], request: Request, websocket: WebSocket = None) -> SIsOk:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    # username = payload.get('username')
    status = await ClientDB.add_task(data=param, user_id=user_id, is_shared=param.is_shared)
    # if param.is_shared:
    #     for client in websocket_clients:
    #         await websocket.send_text(f'Пользователь {username} добавил задание - {param.title}')
    #         await get_task_list(user_id=user_id, websocket=websocket)
    return SIsOk(ok=status)


@tasks.get('/', dependencies=[Depends(valid_cookies)])
async def get_user_tasks(request: Request) -> list[SUserTask]:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    task_list = await ClientDB.get_tasks(user_id=user_id)
    return task_list


@tasks.delete('/delete_task', dependencies=[Depends(valid_cookies)])
async def delete_user_task(task_id: int, request: Request) -> SIsOk:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    status = await ClientDB.delete_user_task_by_id(user_id=user_id, task_id=task_id)
    return SIsOk(ok=status)


@tasks.patch('/update_task_status', dependencies=[Depends(valid_cookies)])
async def update_user_task(task_id: int, status: bool, request: Request) -> SIsOk:
    payload = is_refresh_token(token=request.cookies.get('access_token'))
    user_id = payload.get('sub')
    await ClientDB.update_task_by_id(user_id=user_id, task_id=task_id, status=status)
    return SIsOk(ok=True)


# @tasks.websocket('/task_board')
# async def websocket_board(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_text('Enter your jwt token')
#     token = await websocket.receive_text()
#     status = is_valid_token(token)
#     if not status:
#         await websocket.close(code=1008)
#         return
#     websocket_clients.append(websocket)
#
#     try:
#         while True:
#             await websocket.receive_text()
#             await get_task_list(websocket, user_id=1)
#     except WebSocketDisconnect:
#         websocket_clients.remove(websocket)
