from cassandra.cqlengine import management
from cassandra.cqlengine.management import create_keyspace_simple
from cassandra.cqlengine.connection import _connections
import models
import connection


def create_keyspace_and_table():
    connection.Connection()
    create_keyspace_simple("typeahead_search", replication_factor=1)
    management.sync_table(models.WordCount, keyspaces=["typeahead_search"])


if __name__ == "__main__":
    create_keyspace_and_table()
