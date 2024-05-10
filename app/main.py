from contextlib import asynccontextmanager
import uvicorn

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.core.exception_handlers import custom_http_exception_handler
from app.core.redis_client import Redis
from app.db.CRUD import BaseCRUD
from app.endpoint.tasks import tasks
from app.endpoint.users import users
from app.core.config import settings
from app.middleware.middleware import logging_middleware


# Инициация тестовой базы данных
@asynccontextmanager
async def lifespan(app: FastAPI):
    await BaseCRUD.delete_table()
    print("База отчищена")
    await BaseCRUD.create_table()
    print("База готова к работе")
    yield
    print("Выключение")


@asynccontextmanager
async def lifespan_redis(app: FastAPI):
    print('Проверка подключения Redis...')
    await Redis.connect()
    print('Redis запущен и успешно подключен')
    yield
    await Redis.close()
    print('Соединение с Redis прервано')

app = FastAPI(
    # lifespan=lifespan,
    lifespan=lifespan_redis,
    title="Tasker API",
    summary="Tasker FastApi project",
    version="0.1.0a",
)


app.include_router(users)
app.include_router(tasks)
app.add_exception_handler(HTTPException, custom_http_exception_handler)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware('http')(logging_middleware)

if __name__ == '__main__':
    try:
        uvicorn.run(f"{__name__}:app", port=settings.fast_api_port)
    except KeyboardInterrupt:
        pass
