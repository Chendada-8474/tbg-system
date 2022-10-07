from google.cloud.sql.connector import Connector
from sqlalchemy.ext.declarative import declarative_base
import sqlalchemy
import pymysql

# initialize Connector object
connector = Connector()

# function to return the database connection
def getconn() -> pymysql.connections.Connection:
    conn: pymysql.connections.Connection = connector.connect(
        "cloud-mysql-demo:asia-east1:tbgdemo",
        "pymysql",
        user="root",
        password="ro2231031",
        db="demodb",
    )
    return conn


# create connection pool
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=getconn,
)

Base = declarative_base()
Base.metadata.reflect(pool)


class Authers(Base):
    __table__ = Base.metadata.tables["authors"]


# with pool.connect() as db_conn:
#     # insert into database
#     # query database
#     query = """
#         INSERT INTO demodb.authors (id, name, email) VALUES (3, 'tachih', 'greenhues@gmail.com')
#     """
#     # db_conn.execute(query)
#     result = db_conn.execute("SELECT * FROM demodb.authors").fetchall()

#     # Do something with the results
#     for row in result:
#         print(row)

# connector.close()
if __name__ == "__main__":
    from sqlalchemy.orm import scoped_session, sessionmaker

    db_session = scoped_session(sessionmaker(bind=pool))
    for item in db_session.query(Authers.id, Authers.name, Authers.email).filter(
        Authers.id == 1
    ):
        print(item)
