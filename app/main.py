import os
from contextlib import asynccontextmanager
import uvicorn
from dotenv import load_dotenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import ClientDB
from app.endpoint.tasks import tasks
from app.endpoint.users import users

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ClientDB.delete_table()
    print("База отчищена")
    await ClientDB.create_table()
    print("База готова к работе")
    yield
    print("Выключение")

app = FastAPI(
    # lifespan=lifespan,
    title="Tasker API",
    summary="Tasker FastApi project",
    version="0.1.0a",
)

app.include_router(users)
app.include_router(tasks)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == '__main__':
    try:
        uvicorn.run(f"{__name__}:app", port=int(os.getenv('FAST_API_PORT')))
    except KeyboardInterrupt:
        pass
