# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function
import argparse
import pickle
import os.path
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import base64
from datetime import datetime

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def authenticate(auth_pkl):

    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    # https://developers.google.com/gmail/api/quickstart/python

    if os.path.exists(auth_pkl):
        with open(auth_pkl, 'rb') as token:
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
        with open(auth_pkl, 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    return service


def create_message_with_attachment(
        sender, to, subject, message_text, files):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file: The path to the file to be attached.

    Returns:
        An object containing a base64url encoded email object.
  """

    message = MIMEMultipart()

    if isinstance(to, list):
        message['to'] = ', '.join(to)
    if isinstance(to, str):
        message['to'] = to

    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)

    if isinstance(files, list):
        for file in files:
            fp = open(file, 'r')
            msg = MIMEBase(main_type, sub_type)
            msg.set_payload(fp.read())
            fp.close()

            filename = os.path.basename(file)
            msg.add_header(
                'Content-Disposition',
                'attachment',
                filename=filename)
            message.attach(msg)
    if isinstance(files, str):
        fp = open(file, 'r')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

        filename = os.path.basename(file)
        msg.add_header('Content-Disposition', 'attachment', filename=filename)
        message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(
        message.as_string().encode('UTF-8')).decode('ascii')}


def send_message(service, user_id, message):
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
        message = (service.users().messages().send(userId=user_id, body=message)
                   .execute())
        print('Message Id: {}'.format(message['id']))
        return message
    except HttpError as error:
        print('An error occurred: {}'.format(error))


def run(args_dict):

    date = datetime.now()
    str_date = date.strftime('%m%d_%Y_%H%M')

    auth = authenticate(args_dict['authentication'][0])
    sbj = 'ViralTees: Twitter Trends [{}]'.format(str_date)
    msg = create_message_with_attachment(
        'mitchbregs@gmail.com',
        args_dict['receivers'],
        sbj,
        'ViralTees - Final Test - {}'.format(str_date),
        args_dict['attachments'])

    import pdb; pdb.set_trace()
    return auth, "me", msg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Sending email with attachment via Gmail API.')
    parser.add_argument(
        '-auth', '--authentication',
        required=False,
        nargs=1,
        default=['token.pickle'],
        help="Path to Gmail API authentication credentials pickle file."
    )
    parser.add_argument(
        '-to', '--receivers',
        required=True,
        nargs='*',
        help='Email address of recipient(s).'
    )
    parser.add_argument(
        '-fp', '--attachments',
        required=False,
        nargs='*',
        default=[],
        help='Path to attachment(s).'
    )
    args_dict = vars(parser.parse_args())
    run(args_dict)
