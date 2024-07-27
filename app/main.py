import traceback, asyncio
from fastapi import FastAPI, BackgroundTasks
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.middleware.gzip import GZipMiddleware
from app.routes.main import users_router
from app.routes.cassandra import cassandra_router
from app.routes.trie import trie_router
from app.trie_builder.update_trie import update_trie
from cassandra.cluster import Session
from app.cassandra_utils.connection import get_session_cassandra
from app.cassandra_utils.create_table import create_keyspace_and_table
from app.schemas.response import CustomException
from app.rabbitmq.connection import RabbitMQ
from app.rabbitmq.handler_ps import consume_message


@asynccontextmanager
async def lifespan(app: FastAPI):
    session: Session = get_session_cassandra()
    await update_trie(session)
    await RabbitMQ.get_connection()
    # await start_consuming()
    asyncio.create_task(consume_message())
    yield
    await RabbitMQ.close()
    print("Shuting down Application!!!")


create_keyspace_and_table()
app = FastAPI(
    docs_url="/app/docs",
    #   responses={
    #         400: {"model": BadRequestModel},
    #         404: {"model": NotFoundModel},
    #         401: {"model": UnauthorizedModel},
    #         403: {"model": ForbiddenModel},
    #         409: {"model": ConflictModel},
    #         415: {"model": InvalidMimeTypeModel},
    #     },
    openapi_url="/app/openapi.json",
    redoc_url="/app/redoc/",
    lifespan=lifespan,
)


app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.exception_handler(CustomException)
async def custom_exception_handler(
    request: Request,
    exc: CustomException,
):
    return JSONResponse(status_code=exc.status, content=exc.as_dict())


@app.exception_handler(Exception)
async def server_error_exception_handler(
    request: Request,
    exc: Exception,
):
    return JSONResponse(
        status_code=500,
        content=CustomException(
            detail="Server Error",
            title="Internal Server Error",
            debug_mode=traceback.format_exc().split("\n") if __debug__ else None,
        ).as_dict(),
    )


app.include_router(users_router)
app.include_router(cassandra_router)
app.include_router(trie_router)


# @app.get("/")
# async def root():
#     return {"message": "Hello World hai fdf"}
