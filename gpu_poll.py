#!/usr/bin/env python3

# A hacky script that checks if NVIDIA GPUs are available and sends a notification mail if so.
#
# This uses gmail for sending mails.
# You need to configure your gmail account and generate an authentication token in order to enable the API usage.
# Check https://developers.google.com/gmail/api/quickstart/python for how to do this.
# The generated key is expected at '~/.credentials/client_secret.json'.

import argparse
import os
import io
import subprocess
import time
import datetime

import httplib2
import base64
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from email.mime.text import MIMEText

NUM_GPUS = 4
SCOPES = 'https://www.googleapis.com/auth/gmail.send'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'poll_gpu'
POLL_PERIOD_IN_S = 30

def parseArgs():
    tools.argparser.add_argument("dest_mail_address", help="mail address to send notification mails to")
    tools.argparser.add_argument("--test-send", dest="test_send", action="store_const", const=True, default=False, help="sends a test mail and stops after first poll even if no GPU is free")
    return argparse.ArgumentParser(parents=[tools.argparser]).parse_args()

def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'poll_gpu.json')
    if not os.path.isdir(credential_dir):
        print("ERROR: No directory '{}'.".format(credential_dir))
        exit(1)

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(os.path.join(credential_dir, CLIENT_SECRET_FILE), SCOPES)
        flow.user_agent = APPLICATION_NAME
        credentials = tools.run_flow(flow, store, None)
        print('Storing credentials to ' + credential_path)
    return credentials

def setupMailService():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)
    return service

def createMessage(content, args):
    msg = MIMEText(content)
    msg['to'] = args.dest_mail_address
    msg['from'] = "me"
    if args.test_send:
        msg['subject'] = "Test GPU Detected"
    else:
        msg['subject'] = "Free GPU Detected"
    raw = base64.urlsafe_b64encode(msg.as_bytes())
    return {'raw': raw.decode()}

def sendNotificationMail(service, content, args):
    msg = createMessage(content, args)
    try:
        sent_msg = (service.users().messages().send(userId="me", body=msg).execute())
        print("Sent mail.")
        return sent_msg
    except Exception as error:
        print("ERROR: Failed to send mail: {}".format(error))
        exit(1)

def pollAndNotify(service, args):
    free = False
    print("Polling GPU every {} s...".format(POLL_PERIOD_IN_S))
    while not free:
        ps = subprocess.Popen(('nvidia-smi'), stdout=subprocess.PIPE)
        lines = [line for line in io.TextIOWrapper(ps.stdout, encoding="utf-8")]
        i_start_processes = -1
        for i, line in zip(range(len(lines)), lines):
            if line.startswith("| Processes:"):
                i_start_processes = i
        if i_start_processes != -1:
            n_processes = len(lines) - i_start_processes - 4
            free = (n_processes < NUM_GPUS) or args.test_send
            if free:
                print("{}: Free GPU detected!".format(time.strftime("%d.%m.%Y, %H:%M:%S", time.localtime())))
                # Send nvidia-smi output via mail.
                msg_content = "\n".join(lines)
                sendNotificationMail(service, msg_content, args)
        else:
            print("ERROR: Line 'Processes:' not found in nvidia-smi output.")
        if not free:
            time.sleep(POLL_PERIOD_IN_S)

def main():
    args = parseArgs()
    service = setupMailService()
    pollAndNotify(service, args)

if __name__ == "__main__":
    main()
