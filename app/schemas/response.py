from typing import Generic, TypeVar
from fastapi import HTTPException
from pydantic import BaseModel

NAME_REGEX = r"^[a-zA-Z0-9][a-zA-Z0-9\.\-_\ ]*$"
DataT = TypeVar("DataT")


class BaseResponseModel(BaseModel):
    data: DataT | None = None
    detail: str = ""
    title: str = ""


class CustomException(Exception):
    def __init__(
        self,
        detail: str | None = None,
        title: str | None = None,
        status: int | None = None,
        debug_mode="",
    ):
        self.detail = detail
        self.status = status
        self.title = title
        self.debug_mode = debug_mode

    def as_dict(self):
        return {
            "status": self.status,
            "title": self.title,
            "detail": self.detail,
            "trace": self.debug_mode,
        }

    # debug_mode:str=""
    # status:int=400
    # detail: str=""
    # title: str=""
