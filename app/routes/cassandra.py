import os
from fastapi import APIRouter, Depends
from cassandra.cluster import Session
from ..schemas.response import BaseResponseModel
from ..cassandra_utils import connection, insert_words


cassandra_router = APIRouter(
    prefix="/cassanra",
    tags=["cassandra"],
)


@cassandra_router.post("/insert")
async def insert_words_to_db(
    session: Session = Depends(connection.get_session_cassandra),
) -> BaseResponseModel:
    output_folder_path = os.path.join(os.getcwd(), "app", "hdfs_outputs")
    print(session)
    await insert_words.insert(session, output_folder_path)
    return BaseResponseModel(data="Data inserted successfully")
