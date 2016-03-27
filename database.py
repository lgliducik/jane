from bottle.ext import sqlalchemy as bottle_sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.types import DateTime, UnicodeText, Boolean, Enum, Integer
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = create_engine('sqlite:///documents.db', echo=True)

sql_alchemy_plugin = bottle_sqlalchemy.Plugin(
    engine, # SQLAlchemy engine created with create_engine function.
    Base.metadata, # SQLAlchemy metadata, required only if create=True.
    keyword='db', # Keyword used to inject session database in a route (default 'db').
    create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True, # If it is true, plugin commit changes after route is executed (default True).
    use_kwargs=False # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
)

# class GoogleCode(Base):
#     __tablename__ = 'google_code'
#     id = Column(Integer, Sequence('id_seq'), primary_key=True)
#     auth_code = Column(String(50))
#     google_id = Column(Integer)

#     def __repr__(self):
#         return "<Entity('%d', '%s', '%d')>" % (self.id, self.auth_code, self.google_id)


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
    type_access = Column('type_access', Enum('1','2','3'))
    permission_access = Column('permission_access', Enum('owner','reader','writer'))
    #google_code_id = Column(Integer, ForeignKey('google_code.id'))

def create_db():
    Session = sessionmaker(bind=engine)
    Session.configure(bind=engine) 
    session = Session()
    return session





