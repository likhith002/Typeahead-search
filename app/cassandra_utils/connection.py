from cassandra.cluster import Cluster, Session
from cassandra.cqlengine import connection, management


class Connection:
    def __init__(self):
        # Create a cluster
        self.cluster: Cluster = Cluster(["cassandra"], port=9042)
        self.session: Session = self.cluster.connect(keyspace="typeahead_search")
        connection.register_connection("default", session=self.session, default=True)
        # connection.register_connection("typeahead_search_1", session=self.session)

        # connection.register_connection(name="cassandra_connection", default=True)
        # # Set the default connection
        # connection.set_default_connection("cassandra_connection")

    def close_session(self) -> None:
        self.session.shutdown()


def get_session_cassandra() -> Session:
    conn = Connection()
    print("Created a new connection object")

    return conn.session
