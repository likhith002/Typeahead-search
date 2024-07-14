from fastapi import APIRouter, Depends
from ..trie_builder.update_trie import update_trie, search_word
from cassandra.cluster import Session
from ..cassandra_utils import connection
from ..schemas.response import BaseResponseModel

trie_router = APIRouter(
    prefix="/trie",
    tags=["Trie"],
)


@trie_router.get("/search", response_model=BaseResponseModel)
async def search(word: str) -> BaseResponseModel:
    return BaseResponseModel(
        data=await search_word(word), detail="Search results", title="Trie results"
    )


@trie_router.post("/insert")
async def update_trie_with_latest_tokens(
    session: Session = Depends(connection.get_session_cassandra),
):
    await update_trie(session)
