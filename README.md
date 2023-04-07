# Pair Programming Matchmaker

Given a list of emails in an organization, set up Google calendar meetings to work in pairs.

This could also be used for things like random-1:1's as it just sets up meetings.

If an email has conflicts, it will emit them from the meeting.

## Setup

### Configuration
You can tune the values in `config.json`

### Emails

Add emails to `emails.txt` in a line-separated format, ie.
```
email1@email.com
email2@email.com
email3@email.com
...
```

### Google Calendar integration

You'll need a `credentials.json` file from GCP.

To obtain a `credentials.json` file, follow these steps:
- Go to the Google Cloud Platform Console.
- Click the project drop-down and select or create the project for which you want to add an API key.
- Go to the APIs & Services > Credentials page.
- Click the "Create credentials" button and select "OAuth client ID".
- Choose "Desktop app" as the application type and enter a name for the client.
- Click "Create" to generate the client ID and client secret.
- Click the download button (downward arrow) next to the created client ID to download the credentials.json file.

That's it! Enjoy!
