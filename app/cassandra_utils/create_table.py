from cassandra.cqlengine import management
from cassandra.cqlengine.management import create_keyspace_simple
from cassandra.cluster import Cluster
from cassandra.cqlengine import connection
from .models import WordCount


def create_keyspace_and_table():
    cluster: Cluster = Cluster(["cassandra"], port=9042)
    session = cluster.connect()
    connection.register_connection("default", session=session, default=True)
    create_keyspace_simple("typeahead_search", replication_factor=1)
    management.sync_table(WordCount, keyspaces=["typeahead_search"])


if __name__ == "__main__":
    create_keyspace_and_table()
