from bottle import route, run, template, redirect, request
from beaker.middleware import SessionMiddleware
from google_api import flow, credentials_storage
from apiclient.discovery import build
import httplib2
import bottle
from bottle import HTTPError
from database import GoogleCode, Document, sql_alchemy_plugin
from bottle import get, post, request
#from arrow.arrow import parser

#datetime_parser = parser.DateTimeParser()


app = bottle.Bottle()
app.install(sql_alchemy_plugin)
# Configure the SessionMiddleware
session_opts = {
    'session.type': 'ext:database',
    'session.url':'sqlite:///session.db',
}
app_with_session = SessionMiddleware(app, session_opts)

auth_uri = flow.step1_get_authorize_url()


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
    google_code = db.query(GoogleCode).filter_by(google_id=google_id).first()
    if not google_code:
        google_code = GoogleCode(auth_code=auth_code, google_id=google_id)
        db.add(google_code)

    session['google_id'] = google_id
    session.save()
    return redirect('/')




@app.route('/', method=['POST', 'GET'])
def index(db):
    print '!!!!!!!!!!!!!!request = ', request
    

    session = bottle.request.environ.get('beaker.session')
    user_name = session.get('google_id')
    if user_name is None:
        return redirect(auth_uri)
    else:
        files_info = db.query(Document).all()
        if request.method == 'POST':
            filtr_owner = request.POST.dict['owner'][0]
            print "filtr_owner", filtr_owner
            creation_time = request.POST.dict['creation_time'][0]
            print "creation_time", creation_time
            modification_time = request.POST.dict['modification_time'][0]


            if filtr_owner:
                files_info = db.query(Document).filter(Document.owner == filtr_owner)
            # if creation_time:
            #     files_info = db.query(Document).filter(Document.creation_time = str(creation_time))
            #import ipdb; ipdb.set_trace()
        return template('file_listing', files_info=files_info)


if __name__ == '__main__':
    bottle.run(host='localhost', port=8080, app=app_with_session)

