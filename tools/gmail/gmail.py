import argparse
import base64
import os
from email.mime.text import MIMEText

import httplib2
import oauth2client
import oauth2client.file
from googleapiclient import discovery
from googleapiclient.errors import HttpError
from oauth2client import client, tools

CLIENT_SECRET_FILE = 'gmail_client_secret.json'
APPLICATION_SECRET_FILE = 'weights_app_secret.json'
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
APPLICATION_NAME = 'Weights'


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
    credential_path = os.path.join(credential_dir, APPLICATION_SECRET_FILE)
    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(CLIENT_SECRET_FILE), SCOPES)
        flow.user_agent = APPLICATION_NAME
        flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
        credentials = tools.run_flow(flow, store, flags)
    return credentials


def create_message(to, subject, message_text, sender='bittenweights@gmail.com'):
    """Create a message for an email.

    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      message_text: The text of the email message.

    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEText(message_text)
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode('utf8')}


def get_gmail_service():
    """Returns a gmail service, which can be used to send messages."""
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    return discovery.build('gmail', 'v1', http=http)


def send_message(service, message, user_id='me'):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        #print('Message Id: %s' % message['id'])
        return message
    except HttpError as error_msg:
        raise('Could not send message due to error: ', error_msg)


def test_gmail():
    print('Testing gmail service')
    gmail_service = get_gmail_service()
    print('Service gotten')
    message = create_message('bittenweights@gmail.com', 'test_subject', 'test_message', 'bittenweights@gmail.com')
    print('Message created: ', message)
    send_message(gmail_service, message)
    print('Done. Message sent.')


if __name__ == '__main__':
    test_gmail()