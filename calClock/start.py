from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime
from dateutil.parser import parse
import numpy as np


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.
        
        If nothing has been stored, or if the stored credentials are invalid,
        the OAuth2 flow is completed to obtain the new credentials.
        
        Returns:
        Credentials, the obtained credential.
        """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def getEvents(hours,service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    ahead12 = (datetime.datetime.utcnow()+ datetime.timedelta(hours=hours) ).isoformat() +'Z'
    eventsResult = service.events().list(calendarId='primary', timeMin=now, timeMax=ahead12, maxResults=10, singleEvents=True,orderBy='startTime').execute()
    events = eventsResult.get('items', [])
    return events

def event2LED(events):
    if not events:
        print ('no events')
        return None, None
    else:
        ledColor = np.zeros(48)
        ledEvent = ['']*48
        for event in events:
            start = parse(event['start'].get('dateTime', event['start'].get('dateTime')))
            startTime = start.hour + start.minute/60.
            
            end = parse(event['end'].get('dateTime', event['start'].get('dateTime')))
            endTime = end.hour + start.minute/60.
            
            color = event['colorId'] if 'colorId' in event.keys() else 1

            for x in range( int(startTime*2), int(endTime*2)):
                ledColor[x]=color
                ledEvent[x] = event['summary']

        return ledColor, ledEvent

def lightItUp(colors):
    #Send command to light up clock face
    #Need to worry about nice fading, same color & stacked events, overlap?
    #brightness fades as time is farther away
    pass

def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    events = getEvents(12, service)
    if not events:
         print('No upcoming events found.')
    colors, eventNames = event2LED(events)
    lightItUp(colors)

    for i, color in enumerate(colors):
        print ( i/2.,color,eventNames[i])




if __name__ == '__main__':
    main()
