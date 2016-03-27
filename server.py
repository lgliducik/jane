from bottle import route, run, template, redirect, request
from beaker.middleware import SessionMiddleware
from google_api import flow, credentials_storage
from apiclient.discovery import build
import httplib2
import bottle
from bottle import HTTPError
from database import Document, sql_alchemy_plugin
from bottle import get, post, request
from datetime import datetime
import arrow
import logging


app = bottle.Bottle()
app.install(sql_alchemy_plugin)
# Configure the SessionMiddleware
session_opts = {
    'session.type': 'ext:database',
    'session.url':'sqlite:///session.db',
}
app_with_session = SessionMiddleware(app, session_opts)

auth_uri = flow.step1_get_authorize_url()

logging.basicConfig(filename='logging.log', filemode='w', level=logging.DEBUG, format="%(asctime)s;%(message)s")


def get_time_now():
    now = datetime.now()
    return datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")


def get_user_info(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    people_service = build('people', 'v1', http=http_auth)
    people_resource = people_service.people()
    info = people_resource.get(resourceName='people/me').execute()
    return info['names'][0]['metadata']['source']['id']


@app.route('/auth_result')
def auth_result(db):
    session = bottle.request.environ.get('beaker.session')
    auth_code = request.query.code
    credentials = flow.step2_exchange(auth_code)
    credentials_storage.put(credentials)
    #import ipdb; ipdb.set_trace()

    google_id = get_user_info(credentials)
    # add user
    # google_code = db.query(GoogleCode).filter_by(google_id=google_id).first()
    # if not google_code:
    #     google_code = GoogleCode(auth_code=auth_code, google_id=google_id)
    #     db.add(google_code)

    session['google_id'] = google_id
    session.save()
    return redirect('/')

@app.route('/', method=['POST', 'GET'])
def index(db):
    session = bottle.request.environ.get('beaker.session')
    user_name = session.get('google_id')
    if user_name is None:
        return redirect(auth_uri)
        logging.info('%s, don''t authorized user_name %s', get_time_now(), user_name)
    else:
        logging.info('%s, authorized user_name %s', get_time_now(), user_name)
        files_info = db.query(Document).all()
        filtr_owner = ''
        modification_time_str = ''
        creation_time_str = ''
        header_str = ''
        link_str = ''
        last_modification_author_str = ''
        is_public_access_str = ''
        type_access_str = ''
        permission_access_str = ''
        if request.method == 'POST':
            logging.info('%s, method post', get_time_now())
            filtr_owner = request.POST.dict['owner'][0]
            #print "filtr_owner", filtr_owner
            parser = arrow.parser.DateTimeParser()
            creation_time_str = request.POST.dict['creation_time'][0]
            if creation_time_str:
                creation_time = parser.parse_iso(creation_time_str)
                files_info = db.query(Document).filter(Document.creation_time > creation_time)
            #import ipdb; ipdb.set_trace()
            #print "creation_time", creation_time
            modification_time_str = request.POST.dict['modification_time'][0]
            if modification_time_str:
                modification_time = parser.parse_iso(request.POST.dict['modification_time'][0])
                files_info = db.query(Document).filter(Document.modification_time > modification_time)

            if filtr_owner:
                files_info = db.query(Document).filter(Document.owner.like(
                    '%' + filtr_owner.decode('utf-8') + '%'))

        return template('file_listing', files_info=files_info, owner=filtr_owner, 
                        creation_time=creation_time_str, 
                        modification_time=modification_time_str,
                        header=header_str,
                        link=link_str,
                        last_modification_author=last_modification_author_str,
                        is_public_access=is_public_access_str,
                        type_access=type_access_str,
                        permission_access=permission_access_str,)


if __name__ == '__main__':
    bottle.run(host='localhost', port=8080, app=app_with_session)

