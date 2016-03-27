from oauth2client import client
from oauth2client.file import Storage


credentials_storage = Storage('credentials_file') 

flow = client.flow_from_clientsecrets(
    'client_secret_627083085610-cmckvr8cd88nlrtu53qgopdpaalprnjm.apps.googleusercontent.com.json',
    scope=['https://www.googleapis.com/auth/drive',
           'profile'],
    redirect_uri='http://localhost:8080/auth_result')
flow.params['access_type'] = 'offline'