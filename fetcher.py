from database import Document, engine, create_db, User
from apiclient.discovery import build
import httplib2
from arrow.arrow import parser
from apiclient import errors
import logging
import time
import log
import oauth2client
from oauth2client.contrib.multistore_file import *
import funcy


datetime_parser = parser.DateTimeParser()


def get_documents(credentials, google_id):
    """Get documents from google drive for user.

    Arguments:
    credentials -- to access the Drive API
    google_id -- google id for authorized user
    """

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
                # import ipdb;ipdb.set_trace()
                yield Document(
                    owner=file_['owners'][0]['displayName'],
                    creation_time=datetime_parser.parse_iso(
                                                    file_['createdDate']),
                    modification_time=datetime_parser.parse_iso(
                                                    file_['modifiedDate']),
                    header=file_['title'],
                    link=file_.get('downloadUrl', '...'),
                    last_modification_author=file_['lastModifyingUserName'],
                    is_public_access=file_['shared'],
                    type_access=u'1',
                    permission_access=file_['userPermission']['role'],
                    google_code_id=google_id
                    )
            page_token = files.get('nextPageToken')
            if not page_token:
                break
        except errors.HttpError as error:
            print 'An error occurred: %s' % error
            break

db = create_db()


@funcy.once
def set_trace():
    import pdb
    pdb.set_trace()


def main():
    count = 0
    count_files = 0
    while True:
        time.sleep(5)
        credential_keys = get_all_credential_keys('test_storage.txt')
        for key in credential_keys:
            user_info = db.query(User).filter(
                            User.google_id == key['clientId']).first()
            if not user_info:
                user_info = User(
                                google_id=key['clientId'],
                                is_download_data=False)
                db.add(user_info)
                db.commit()
                user_info = db.query(User).filter(
                            User.google_id == key['clientId']).first()
                logging.info(
                            'user_info.is_download_data = %s',
                            user_info.is_download_data)
            if not user_info.is_download_data: # user_info.is_download_data == False
                logging.info(
                            'user_info.is_download_data = %s',
                            user_info.is_download_data)
                logging.info(
                            'download files from google id %s',
                            key['clientId'])
                storage = get_credential_storage(
                    'test_storage.txt',
                    key['clientId'],
                    key['userAgent'],
                    key['scope'])
                credentials = storage.get()
                while credentials and count == 0:
                    for document in get_documents(
                                            credentials, key['clientId']):
                        db.add(document)
                        count_files = count_files + 1
                    db.commit()
                    count = count + 1
                    break
                logging.info('download count = %d files from google id %s',
                             count_files, key['clientId'])

                user_info = db.query(User).filter(
                            User.google_id == key['clientId']).first()
                #set_trace()
                if user_info:
                    if user_info.is_download_data:
                        user_info.is_download_data = True
                        logging.info(
                            '!!!!!!!!!!!!!!user_info.is_download_data = %s',
                            user_info.is_download_data)
                        db.commit()
                count_files = 0
                count = 0

if __name__ == "__main__":
    main()
