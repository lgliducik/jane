from bottle import route, run, template, redirect, request

from beaker.middleware import SessionMiddleware

from oauth2client import client

from apiclient.discovery import build

import httplib2

import bottle
from bottle import HTTPError
from bottle.ext import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, Sequence, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
engine = create_engine('sqlite:///:memory:', echo=True)

app = bottle.Bottle()

sql_alchemy_plugin = sqlalchemy.Plugin(
    engine, # SQLAlchemy engine created with create_engine function.
    Base.metadata, # SQLAlchemy metadata, required only if create=True.
    keyword='db', # Keyword used to inject session database in a route (default 'db').
    create=True, # If it is true, execute `metadata.create_all(engine)` when plugin is applied (default False).
    commit=True, # If it is true, plugin commit changes after route is executed (default True).
    use_kwargs=False # If it is true and keyword is not defined, plugin uses **kwargs argument to inject session database (default False).
)

app.install(sql_alchemy_plugin)

# Configure the SessionMiddleware
session_opts = {
    'session.type': 'ext:database',
    'session.url':'sqlite:///:memory:',
}
app_with_session = SessionMiddleware(app, session_opts)

class Entity(Base):
    __tablename__ = 'users'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    name = Column(String(50))
    google_id = Column(Integer)

    def __init__(self, name, google_id):
        self.name = name
        self.google_id = google_id

    def __repr__(self):
        return "<Entity('%d', '%s', '%d')>" % (self.id, self.name, self.google_id)


flow = client.flow_from_clientsecrets(
    'client_secret_627083085610-cmckvr8cd88nlrtu53qgopdpaalprnjm.apps.googleusercontent.com.json',
    scope=['https://www.googleapis.com/auth/drive.metadata.readonly',
           'profile'],
    redirect_uri='http://localhost:8080/auth_result')

auth_uri = flow.step1_get_authorize_url()


# http://localhost:8080/?code=4/lzPCOLHcTW5opdekOIANjv-jiGtoyJMN-y2o1Q0UBHs#


def get_files(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v3', http=http_auth)
    files = drive_service.files().list().execute()


def get_user_info(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    people_service = build('people', 'v1', http=http_auth)
    people_resource = people_service.people()
    info = people_resource.get(resourceName='people/me').execute()
    return info['names'][0]['metadata']['source']['id']



@app.route('/auth_result')
def auth_result(db):
    session = bottle.request.environ.get('beaker.session')
    #return template('hello_template', name=name)
    auth_code = request.query.code
    # print auth_code
    # import ipdb;ipdb.set_trace()
    print request.cookies.dict
    credentials = flow.step2_exchange(auth_code)
    # import ipdb; ipdb.set_trace()
    # x = 1
    #redirect('/')

    google_id = get_user_info(credentials)
    # add user
    entity = db.query(Entity).filter_by(google_id=google_id).first()
    if not entity:
        entity = Entity(auth_code, google_id)
        db.add(entity)
        session['google_id'] = google_id
        session.save()

        # show user
        entity = db.query(Entity).filter_by(name=auth_code).first()
        if entity:
            print {'id': entity.id, 'name': entity.name, 'google_id': entity.google_id}

        print 'google_id = ', google_id

    return template('hello_template', name='lida')


@app.route('/')
def index():
    session = bottle.request.environ.get('beaker.session')
    user_name = session.get('google_id')
    if user_name is None:
        return redirect(auth_uri)
    else:
        return "Hello {}".format(user_name)


if __name__ == '__main__':
    bottle.run(host='localhost', port=8080, app=app_with_session)

