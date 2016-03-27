from database import Document, engine, create_db
from apiclient.discovery import build
from google_api import flow, credentials_storage
import httplib2
from arrow.arrow import parser 
from apiclient import errors
import logging
from datetime import datetime
import time
# create formatter
#formatter = logging.Formatter("%(asctime)s;%(message)s")

# add formatter to ch
#ch.setFormatter(formatter)


# def get_time_now():
#     now = datetime.now()
#     return datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S")

logging.basicConfig(filename='logging_fetcher.log', filemode='w', level=logging.DEBUG, format="%(asctime)s;%(message)s")

datetime_parser = parser.DateTimeParser()


# header = Column(Text())
# link = Column(Text())
# last_modification_author = Column(Text())
# is_public_access = Column(Boolean())
# type_access = Column('type_access', Enum('1','2','3'))
# permission_access = Column('permission_access', Enum('owner','reader','writer'))
# google_code_id = Column(Integer, ForeignKey('google_code.id'))

def get_documents(credentials):
    logging.info('get documents')
    auth_code = credentials.authorize(httplib2.Http())
    drive_service = build('drive', 'v2', http=auth_code)
    files_resource = drive_service.files()
    page_token = None
    while True:
        try:
            param = {}
            if page_token:
                param['pageToken'] = page_token
            files = files_resource.list(**param).execute()

            for file_ in files['items']:
                #import ipdb;ipdb.set_trace()
                yield Document(
                    owner=file_['owners'][0]['displayName'], 
                    creation_time=datetime_parser.parse_iso(file_['createdDate']),
                    modification_time=datetime_parser.parse_iso(file_['modifiedDate']),
                    header = file_['title'],
                    link = file_.get('downloadUrl', '...'),
                    last_modification_author = file_['lastModifyingUserName'],
                    is_public_access = file_['shared'],
                    type_access = u'1' ,
                    permission_access = file_['userPermission']['role']
                    )


            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print 'An error occurred: %s' % error
            break

session = create_db()

count = 0
while True:
    time.sleep(5)
    credentials = credentials_storage.get()
    if credentials and count == 0:
        for document in get_documents(credentials):
            logging.info('add credentials to file')
            session.add(document)
        session.commit()
        count = count + 1
        break