from typing import List
from cassandra.cluster import Session
from ..cassandra_utils.models import WordCount
from .trie import initialize_trie


def fetch_all_entries():
    return WordCount.objects().all()


async def update_trie(session: Session | None = None) -> None:
    """Update trie logic"""
    # print('trie updated successfully')
    rows = fetch_all_entries()
    _trie, _ = initialize_trie()
    for row in rows:
        print(*row.values())
        _trie.insert(row.word, row.count)


async def search_word(word: str) -> List[str]:
    _trie, _ = initialize_trie()
    return _trie.serach(word)
