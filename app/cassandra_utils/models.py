from cassandra.cqlengine.columns import UUID, Text, BigInt
from cassandra.cqlengine.models import Model
from uuid import uuid4


class WordCount(Model):
    __keyspace__ = "typeahead_search"
    id = UUID(primary_key=True, default=uuid4)
    word = Text()
    count = BigInt()
