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
import time
import math

from neopixel import *

# LED strip configuration:
LED_COUNT      = 24      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)


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
        return None, None
    else:
        ledColor = np.zeros(48)
        ledEvent = ['']*48
        for event in events:
            start = parse(event['start'].get('dateTime', event['start'].get('dateTime')))
            startTime = start.hour + start.minute/60.
            
            end = parse(event['end'].get('dateTime', event['start'].get('dateTime')))
            endTime = end.hour + end.minute/60.
#            print (startTime, endTime)
            color = event['colorId'] if 'colorId' in event.keys() else 1
            if startTime<endTime:
                for x in range( int(math.floor(startTime*2)), int(math.ceil(endTime*2)) ):
                    ledColor[x]=color
                    ledEvent[x] = event['summary']
            else:
                for x in range( int(math.floor(startTime*2)), 48):
                    ledColor[x]=color
                    ledEvent[x] = event['summary']
                for y in range( 0, int(math.ciel(endTime*2))):
                    ledColor[y]=color
                    ledEvent[y] = event['summary']

        return ledColor, ledEvent

def getColor(color, version):
    colors = [[Color(0,0,0)],#0
              [Color(180, 40, 255)],#1
              [Color(255, 10, 100)],#2
              [Color(59, 155, 141)],#3
              [Color(106, 242, 106)],#4
              [Color(204, 181, 30)],#5
              [Color(133, 242, 50)],#6
              [Color(204, 36, 80)],#7
              [Color(255, 255, 255)],#8
              [Color(40, 10, 255)],#9
              [Color(255, 0, 0)],#10
              [Color(0, 200, 0)],#11
              ]
    try:
        return colors[color][version]
    except:
        return Color(255,255,255)


def lightItUp(colors,strip):
    hour=datetime.datetime.now().hour - 4 + datetime.datetime.now().minute / 60.
    for j in range(int(hour*2),int(hour*2+24)):
        i=j%48

        strip.setPixelColor( i%24, getColor(int(colors[i]),0) )
        
        strip.setBrightness(100)
        strip.show()
    #Send command to light up clock face
    #Need to worry about nice fading, same color & stacked events, overlap?
    #brightness fades as time is farther away


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)
    
    strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
    strip.begin()
    oldColors=None
    
    while True:
        events = getEvents(12, service)
        if not events:
#            print('No upcoming events found.')
            colors=np.zeros(48)
        else:
            colors, eventNames = event2LED(events)
        if  not (np.array_equal(colors, oldColors)):
            lightItUp(colors,strip)

#            if colors.any():
#                for i, color in enumerate(colors):
#                    print ( i/2.,color,eventNames[i])
            oldColors=colors
        time.sleep(1)




if __name__ == '__main__':
    main()
