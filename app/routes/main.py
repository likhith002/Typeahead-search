import os
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from typing import List, Annotated, Literal
from app.schemas.response import BaseResponseModel
from app.schemas.user import CreateUserReq, UserResponse, User

from sqlalchemy.orm import Session
from app.utils import get_password_hash, write_to_file
from app.hadoop import (
    submit_mapreduce_job,
    upload_file_to_hdfs,
    download_outputs_folder,
)

users_router = APIRouter(
    prefix="/hdfs",
    tags=["Hadoop"],
)

users = []


@users_router.get("/create-job", description="Trigger MR Job")
async def create_job(q: str = Query(default="univ")) -> BaseResponseModel:
    # write_to_file(q)
    file_path = os.path.join(os.getcwd(), "app", "static", "text.txt")
    await submit_mapreduce_job({"input_file": file_path, "output_dir": "/outputs"})


@users_router.post("/upload", description="Upload file from local to hdfs")
async def upload_to_hdfs() -> BaseResponseModel:
    file_path = os.path.join(os.getcwd(), "app", "static", "text.txt")
    await upload_file_to_hdfs(file_path)


@users_router.get("/download", description="Download file from hdfs to local")
async def download_outputs_to_local():
    local_folder_path = os.path.join(os.getcwd(), "app", "hdfs_outputs")
    hdfs_output_folder_path = "/output"
    await download_outputs_folder(local_folder_path, hdfs_output_folder_path)
