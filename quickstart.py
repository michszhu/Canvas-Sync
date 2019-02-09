from __future__ import print_function
import datetime
import pickle
import os.path
import csv
import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
CAL_ID = 'rtpri0j3p4skqibte917a4g730@group.calendar.google.com'


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.

    creds = None

    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    print_events(service)

    del_events(service)
    #make_event(service)
    #parse(service)

def parse(service):
    arr = []
    with open('Book1.csv', encoding = 'ascii', errors = 'ignore') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',') #, encoding='ascii'
        line_count = 0
        prev_row = []
        for row in csv_reader:
            new_row = []
            for c in range(len(row) - 1):
                if row[c] == '': #use prev row info when cell empty
                    new_row.append(prev_row[c])
                else:
                    new_row.append(row[c])
            arr.append(new_row)
            prev_row = new_row
            line_count += 1

        print(*arr, sep = '\n')

    add_events(service, arr)

def add_events(service, events):
    properties = []
    for prop in events[0]:
        properties.append(prop)

    for event_index in range(1, len(events)):
        event = events[event_index]
        #dictionary of properties
        description = {}
        c = 0
        for c in range(len(event)):
            description[properties[c]] = event[c]
            c += 1
        print(description)
        make_event(service, description)



def print_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = service.events().list(calendarId= CAL_ID, timeMin=now,
                                        maxResults=10, singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'])


def del_events(service):
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    events_result = service.events().list(calendarId= CAL_ID, timeMin=now,
                                        singleEvents=True,
                                        orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        id = event['id']
        print(id, event['summary'])
        service.events().delete(calendarId=CAL_ID, eventId=id).execute()

def make_event(service, event):
    now = datetime.datetime.utcnow().isoformat()
    print(now)
    event = {
    'summary': event['Course'],
    'location': event['Bldg'] + ' ' + event['Room'],
    'description': event['Title'],
    'start': {
        'dateTime': now,
        'timeZone': 'America/Chicago',
    },
    'end': {
        'dateTime': '2019-05-28T17:00:00',
        'timeZone': 'America/Chicago',
    },
    'recurrence': [
        'RRULE:FREQ=WEEKLY;COUNT=2;BYDAY=TU'
    ]
    }

    event = service.events().insert(calendarId=CAL_ID, body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))







if __name__ == '__main__':
    main()