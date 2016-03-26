from bottle import route, run, template, redirect, request

from beaker.middleware import SessionMiddleware

from google_api import flow, credentials_storage


from apiclient.discovery import build

import httplib2

import bottle
from bottle import HTTPError


from database import GoogleCode, Document, sql_alchemy_plugin





app = bottle.Bottle()



app.install(sql_alchemy_plugin)

# Configure the SessionMiddleware
session_opts = {
    'session.type': 'ext:database',
    'session.url':'sqlite:///:memory:',
}
app_with_session = SessionMiddleware(app, session_opts)






auth_uri = flow.step1_get_authorize_url()


# http://localhost:8080/?code=4/lzPCOLHcTW5opdekOIANjv-jiGtoyJMN-y2o1Q0UBHs#


# def get_files(credentials):
#     http_auth = credentials.authorize(httplib2.Http())
#     drive_service = build('drive', 'v3', http=http_auth)
#     files = drive_service.files().list().execute()


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
    #print request.cookies.dict
    credentials = flow.step2_exchange(auth_code)
    
    credentials_storage.put(credentials)

    #import ipdb; ipdb.set_trace()
    # import ipdb; ipdb.set_trace()
    # x = 1
    #redirect('/')

    google_id = get_user_info(credentials)
    # add user
    google_code = db.query(GoogleCode).filter_by(google_id=google_id).first()
    if not google_code:
        google_code = GoogleCode(auth_code=auth_code, google_id=google_id)
        db.add(google_code)
        session['google_id'] = google_id
        session.save()


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

