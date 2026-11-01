from pymongo import MongoClient
from cassandra.cluster import Cluster


def connect_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client.restodb

    client.admin.command('ping')

    print("MongoDB connected successfully")
    return client, db


def connect_cassandra():
    cluster = Cluster(['127.0.0.1'])
    session = cluster.connect()

    print("Cassandra connected successfully")
    return cluster, session


if __name__ == "__main__":
    mongo_client = None
    cassandra_cluster = None

    try:
        mongo_client, db = connect_mongodb()
        cassandra_cluster, session = connect_cassandra()

    except Exception as error:
        print(f"Connection error: {error}")

    finally:
        if mongo_client is not None:
            mongo_client.close()

        if cassandra_cluster is not None:
            cassandra_cluster.shutdown()