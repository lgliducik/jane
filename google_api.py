from oauth2client import client


scope = ['https://www.googleapis.com/auth/drive',
         'profile']
flow = client.flow_from_clientsecrets(
    'client_secret_627083085610-cmckvr8cd88nlrtu53qgopdpaalprnjm.apps.googleusercontent.com.json',
    scope=scope,
    redirect_uri='http://jane.mitroshina.info/auth_result')
flow.params['access_type'] = 'offline'
