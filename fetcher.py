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
        # file_info = files_resource.get(fileId=file_['id']).execute()
        # print file_['id']
        # import ipdb; ipdb.set_trace()
        yield Document(
            owner=file_['owners'][0]['displayName'], 
            creation_time=datetime_parser.parse_iso(file_['createdDate']),
            modification_time=datetime_parser.parse_iso(file_['modifiedDate']))



#     raise HttpAccessTokenRefreshError(error_msg, status=resp.status)
# oauth2client.client.HttpAccessTokenRefreshError: invalid_grant

session = create_db()
#google_codes = session.query(GoogleCode).all()
#print google_codes
#for google_code in google_codes:

credentials = credentials_storage.get()
for document in get_documents(credentials):
    session.add(document)
session.commit()

    #import ipdb; ipdb.set_trace()
    
    #print "files", get_files(credentials)
    #import ipdb; ipdb.set_trace()
    #document = Documents(owner=list_files, header=google_id)
    #db.add(document)

    # owner 
    # header 
    # link = Column(Text())
    # creation_time = Column(DateTime())
    # modification_time = Column(DateTime())
    # last_modification_author = Column(Text())
    # is_public_access = Column(Boolean())
    # type_access = Column('type_access', Enum('1','2','3'))
    # permission_access = Column('permission_access', Enum('owner','reader','writer'))
    # google_code_id = Column(Integer, ForeignKey('google_code.id'))

    #if not google_code: