import random
import itertools
from datetime import datetime, timedelta, time
import pytz
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from typing import List
import json

# Function to read the configuration from a file
def read_config_from_file(filename: str) -> dict:
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

config = read_config_from_file('config.json')
# Parse the meeting date, time, duration, and timezone
meeting_date = datetime.strptime(config['meeting_date'], '%Y-%m-%d').date()
meeting_time = datetime.strptime(config['meeting_time'], '%H:%M').time()
duration_minutes = config['duration_minutes']
timezone = config['timezone']
# Combine the date and time, and localize it to the specified timezone
meeting_datetime = datetime.combine(meeting_date, meeting_time)
meeting_datetime = pytz.timezone(timezone).localize(meeting_datetime)

# Function to read emails from a file
def read_emails_from_file(filename: str) -> List[str]:
    with open(filename, 'r') as file:
        emails = [line.strip() for line in file.readlines()]
    return emails

# Read the emails from the 'emails.txt' file
emails = read_emails_from_file('emails.txt')

# Function to check for meeting conflicts
def check_conflicts(service, emails: List[str], meeting_time, duration_minutes, timezone: str) -> List[str]:
    start_time = meeting_time.isoformat()
    end_time = (meeting_time + timedelta(minutes=duration_minutes)).isoformat()

    freebusy_request = {
        "timeMin": start_time,
        "timeMax": end_time,
        "timeZone": timezone,
        "items": [{"id": email} for email in emails],
    }

    freebusy_response = service.freebusy().query(body=freebusy_request).execute()
    conflicts = [
        email
        for email, calendar in freebusy_response['calendars'].items()
        if calendar.get("busy")
    ]

    return conflicts

# Function to create random pairs
def create_random_pairs(emails):
    random.shuffle(emails)
    pairs = list(itertools.zip_longest(emails[::2], emails[1::2]))
    return pairs

def create_meet_events(service, pairs, meeting_time, duration_minutes, timezone: str):
    event_results = []

    # Filter out pairs with a None value
    pairs = [pair for pair in pairs if all(pair)]

    for pair in pairs:
        attendees = [{'email': pair[0]}, {'email': pair[1]}]

        start_time = meeting_time.isoformat()
        end_time = (meeting_time + timedelta(minutes=duration_minutes)).isoformat()

        event = {
            'summary': f"Pair Programming {pair[0]} leads, {pair[1]} follows",
            'start': {
                'dateTime': start_time,
                'timeZone': timezone,
            },
            'end': {
                'dateTime': end_time,
                'timeZone': timezone,
            },
            'attendees': attendees,
            'conferenceData': {
                'createRequest': {
                    'requestId': f"meet-{pair[0]}-{pair[1]}",
                },
            },
            'reminders': {
                'useDefault': True,
            },
        }

        event = service.events().insert(calendarId='primary', body=event, conferenceDataVersion=1).execute()
        event_results.append(event)

    return event_results


# Set up the Google Calendar API
creds = None
if creds and creds.expired and creds.refresh_token:
    creds.refresh(Request())
else:
    flow = InstalledAppFlow.from_client_secrets_file('credentials.json', ['https://www.googleapis.com/auth/calendar'])
    creds = flow.run_local_server(port=0)

service = build('calendar', 'v3', credentials=creds)

# Check for meeting conflicts and remove conflicted emails
conflicts = check_conflicts(service, emails, meeting_datetime, duration_minutes, timezone)

if conflicts:
    print("The following users have meeting conflicts:")
    for email in conflicts:
        print(f"- {email}")
    emails = [email for email in emails if email not in conflicts]

# Create the meeting pairs and events
pairs = create_random_pairs(emails)
meet_events = create_meet_events(service, pairs, meeting_datetime, duration_minutes, timezone)

# Print the results
for event in meet_events:
    print(f"{event['attendees'][0]['email']} and {event['attendees'][1]['email']} - {event['hangoutLink']}")
