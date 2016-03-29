from bottle.ext import sqlalchemy as bottle_sqlalchemy
from sqlalchemy import (
    create_engine,
    Column,
    Sequence,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, UnicodeText, Boolean, Enum, Integer
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///documents.db')

sql_alchemy_plugin = bottle_sqlalchemy.Plugin(
    engine,         # SQLAlchemy engine created with create_engine function.
    Base.metadata,  # SQLAlchemy metadata, required only if create=True.
    keyword='db',   # Keyword used to inject session database in a route
                    # (default 'db').
    create=False,   # If it is true, execute `metadata.create_all(engine)`
                    # when plugin is applied (default False).
    commit=True,    # If it is true, plugin commit changes after route is
                    # executed (default True).
    use_kwargs=False    # If it is true and keyword is not defined, plugin uses
                        # **kwargs argument to inject session database
                        # (default False).
)


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    google_id = Column(Integer)
    is_download_data = Column(Boolean)


class Document(Base):
    __tablename__ = 'documents'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    owner = Column(UnicodeText())
    creation_time = Column(DateTime())
    modification_time = Column(DateTime())
    header = Column(UnicodeText())
    link = Column(UnicodeText())
    last_modification_author = Column(UnicodeText())
    is_public_access = Column(Integer())
    type_access = Column('type_access', Enum('1', '2', '3'))
    permission_access = Column(
        'permission_access',
        Enum('owner', 'reader', 'writer'))
    google_code_id = Column(Integer)


def create_db():
    Base.metadata.create_all(engine, checkfirst=True)
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine)
    session = Session()
    return session
