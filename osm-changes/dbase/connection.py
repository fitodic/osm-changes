from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base

user = ''
password = ''
host = ''
port = ''
database = ''
schema = ''

engine = create_engine('postgresql+psycopg2://%s:%s@%s:%s/%s' %
                       (user, password, host, port, database),
                       echo=False)

session = scoped_session(sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine))

Base = declarative_base()
Base.query = session.query_property()
Base.metadata.schema = schema
