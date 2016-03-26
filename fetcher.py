from database import GoogleCode, Document, engine, create_db
from apiclient.discovery import build
from google_api import flow, credentials_storage
import httplib2
from arrow.arrow import parser 


datetime_parser = parser.DateTimeParser()


def get_documents(credentials):
    auth_code = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v2', http=auth_code)
    files_resource = drive_service.files()
    files = files_resource.list().execute()
    # import ipdb; ipdb.set_trace()
    for file_ in files['items']:
        # import ipdb; ipdb.set_trace()
        yield Document(
            owner=file_['owners'][0]['displayName'], 
            creation_time=datetime_parser.parse_iso(file_['createdDate']),
            modification_time=datetime_parser.parse_iso(file_['modifiedDate']))

#     raise HttpAccessTokenRefreshError(error_msg, status=resp.status)
# oauth2client.client.HttpAccessTokenRefreshError: invalid_grant

session = create_db()

credentials = credentials_storage.get()
for document in get_documents(credentials):
    session.add(document)
session.commit()