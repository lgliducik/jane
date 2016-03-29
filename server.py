from bottle import route, run, template, redirect, request
from beaker.middleware import SessionMiddleware
from google_api import flow, scope
from apiclient.discovery import build
import httplib2
import bottle
from bottle import HTTPError
from database import Document, sql_alchemy_plugin, User, create_db
from bottle import get, post, request
from datetime import datetime
import arrow
import logging
import funcy
import oauth2client
from oauth2client.contrib.multistore_file import get_credential_storage
import log


app = bottle.Bottle()
app.install(sql_alchemy_plugin)
# Configure the SessionMiddleware
session_opts = {
    'session.type': 'ext:database',
    'session.url': 'sqlite:///session.db',
}
app_with_session = SessionMiddleware(app, session_opts)

db = create_db()

auth_uri = flow.step1_get_authorize_url()


def get_user_info(credentials):
    """Get user info from credentials.

    Arguments:
    credentials -- to access the Drive API
    """

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
    google_id = get_user_info(credentials)
    session['google_id'] = google_id
    session.save()
    storage = get_credential_storage(
                                    'test_storage.txt',
                                    google_id,
                                    'user_agent',
                                    scope)
    # import ipdb; ipdb.set_trace()
    storage.put(credentials)
    if not db.query(User).filter_by(google_id=google_id).first():
        user = User(google_id=google_id, is_download_data=False)
        db.add(user)
        db.commit()
    return redirect('/')


@funcy.once
def set_trace():
    import ipdb
    ipdb.set_trace()


@app.route('/', method=['POST', 'GET'])
def index(db):
    session = bottle.request.environ.get('beaker.session')
    user_name = session.get('google_id')
    if user_name is None:
        return redirect(auth_uri)
        logging.info('don''t authorized user_name %s', user_name)
    else:
        logging.info('authorized user_name %s', user_name)
        files_info = db.query(Document).filter(
                                    Document.google_code_id == user_name).all()
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
            logging.info('filtering files')
            filtr_owner = request.POST.dict['owner'][0]
            parser = arrow.parser.DateTimeParser()
            creation_time_str = request.POST.dict['creation_time'][0]
            if creation_time_str:
                creation_time = parser.parse_iso(creation_time_str)
                files_info = db.query(Document).filter(
                                        Document.creation_time > creation_time)
            modification_time_str = request.POST.dict['modification_time'][0]
            if modification_time_str:
                modification_time = parser.parse_iso(
                                    request.POST.dict['modification_time'][0])
                files_info = db.query(Document).filter(
                                Document.modification_time > modification_time)

            if filtr_owner:
                files_info = db.query(Document).filter(Document.owner.like(
                    '%' + filtr_owner.decode('utf-8') + '%'))

        return template('file_listing', files_info=files_info,
                        owner=filtr_owner,
                        creation_time=creation_time_str,
                        modification_time=modification_time_str,
                        header=header_str,
                        link=link_str,
                        last_modification_author=last_modification_author_str,
                        is_public_access=is_public_access_str,
                        type_access=type_access_str,
                        permission_access=permission_access_str,
                        user_name=str(user_name))


if __name__ == '__main__':
    bottle.run(host='localhost', port=8080, app=app_with_session)
