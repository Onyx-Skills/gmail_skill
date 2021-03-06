from adapt.intent import IntentBuilder
from onyx.messagebus.message import Message

from onyx.skills.core import OnyxSkill
from onyx.util.log import getLogger
from onyx.util import record, play_mp3

import httplib2
import os
from os.path import dirname, abspath, join, expanduser
import sys

from googleapiclient import discovery
from googleapiclient import errors
import oauth2client
from oauth2client import file
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from oauth2client.client import OAuth2WebServerFlow

import json
from json import JSONEncoder
from html.parser import HTMLParser
from datetime import datetime

logger = getLogger(dirname(__name__))
sys.path.append(abspath(dirname(__file__)))

__author__ = 'j c a soft'

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'
CID = "62819934886-fdlah5snmvvh5ibaghl7l9gd6dj5is30.apps.googleusercontent.com"
CIS = "27NYpsIihC1e4GSmg6t2hqbc"
APPLICATION_NAME = 'Onyx Gmail'

loginEnabled = ""
max_results = 10
#time_format = 12

python_out 		=  "/usr/bin/python2.7"
third_party_skill	= expanduser("~")+"/skills/gmail_skill/"
effects 		= third_party_skill + "effects/"


def get_credentials():
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    print("checking for cached credentials")
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,'onyx-gmail-skill.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        credentials = tools.run_flow(OAuth2WebServerFlow(client_id=CID,client_secret=CIS,scope=SCOPES,user_agent=APPLICATION_NAME),store)
        print ('Storing credentials to ' + credential_dir)
        print( 'Your GMail Skill is now authenticated ')
    else:
        print ('Loaded credentials for Gmail Skill from ' + credential_dir)

    return credentials



def loggedIn():
    """
    Future implementation
    To do:
	- Verify FaceLogin Skill
	- Verify ProximityLogin Skill (For use with SmartPhone Onyx Client App and iBeacon function on Rpi)
	- Verify PhoneClientLogin Skill (For use with SmartPhone Onyx Client App with fingerprint or Unlock code )
	- Maybe VoiceLogin Skill
    """
    return True



def main(max_results):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    global service
    service = discovery.build('gmail', 'v1', http=http)

    try:
        user_id = "me"
        label_id = ["INBOX","IMPORTANT"]
        query = "is:unread"

        response = service.users().messages().list(userId=user_id,labelIds=label_id,maxResults=max_results,q=query).execute()

        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])
        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,labelIds=label_id,maxResults=max_results,q=query,pageToken=page_token).execute()
		# messages.extend(response['messages'])

        return messages

    except errors.HttpError as error:
        print ('An error occurred: %s' % error)



def GetMessage(user_id, msg_id):
	try:
		message = service.users().messages().get(userId=user_id, id=msg_id).execute()
		return message

	except errors.HttpError as error:
		print( 'An error occurred: %s' % error)


def parse_datetime_string(string):
    if '+' in string:
        if "UTC" in string or "GMT" in string or "EST" in string or "PST" in string or "MEZ" in string:
            string = string[:-6]
            return datetime.strptime(string,"%a, %d %b %Y %H:%M:%S +%f")
    elif '-' in string:
        if "UTC" in string or "GMT" in string or "EST" in string or "PST" in string or "MEZ" in string:
            string = string[:-6]
            return datetime.strptime(string,"%a, %d %b %Y %H:%M:%S -%f")
    else:
        string = string[:-6]
        return datetime.strptime(string,"%a, %d %b %Y %H:%M:%S +%f")

class GoogleGmailSkill(OnyxSkill):
    """
    A Skill to check your google calendar
    also can add events
    """

    global user_id
    user_id = "me"

    def google_gmail(self, msg=None):
        argv = sys.argv
        sys.argv = []
        self.credentials = get_credentials()
        http = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('calendar', 'v3', http=http)
        sys.argv = argv


    def GetMails(self,msgs, max_results, detail):

    	msgs = msgs[:max_results]

    	if (max_results > len(msgs)):
    		max_results = len(msgs)

    	complete_phrase = ""
    	for x in range(0,max_results):
    		msg_id = msgs[x]["id"]
    		msg = GetMessage(user_id, msg_id)
    		msg_headers = msg["payload"]["headers"]
    		msg_headersT = {}
    		for p in msg_headers: msg_headersT[p["name"]] = p["value"]
    		msg_from 	= msg_headersT["From"]
    		msg_from 	= msg_from.split("<")
    		if (len(msg_from) > 1):
    			if msg_from[0][:1] == '"':
    				msg_from_sender = msg_from[0][1:-2]
    			else:
    				msg_from_sender = msg_from[0]
    			msg_from_email	= msg_from[1][0:-1]
    		else:
    			msg_from_email	= msg_from[0][0:-1]

    		msg_from_sender = msg_from_sender.replace('. ',', ')

    		msg_received	= parse_datetime_string(msg_headersT["Date"])
    		msg_received_24	= msg_received.strftime("%A, %B %d, %Y at %H:%M")
    		msg_received_12 = msg_received.strftime("%A, %B %d, %Y at %I:%M %p")

    		if int(time_format) == 12:
    			msg_received = msg_received_12
    		else:
    			msg_received = msg_received_24

    		msg_subject 	= HTMLParser().unescape(msg_headersT["Subject"])
    		msg_txt		= HTMLParser().unescape(msg["snippet"])

    		complete_phrase = "Email from "+msg_from_sender+" received "+msg_received+", with subject, "+msg_subject
    		if detail is True:
    			complete_phrase = complete_phrase + ", Message, " + msg_txt

    		self.speak(complete_phrase, self.lang)




    def __init__(self):
        super(GoogleGmailSkill, self).__init__('GoogleGmailSkill')
        self.loginEnabled = True
        self.maxResults = 10 
        self.time_format = 12

        global python_out
        global third_party_skill
        global effects
        global time_format

        loginEnabled = self.loginEnabled
        max_results = self.maxResults
        time_format = self.time_format


    def initialize(self):
        self.load_data_files(dirname(__file__))

        self.emitter.on(self.name + '.google_gmail',self.google_gmail)
        self.emitter.emit(Message(self.name + '.google_gmail'))

        intent = IntentBuilder('CheckGmailIntent')\
            .require('CheckKeyword') \
            .require('GMailKeyword') \
            .build()
        self.register_intent(intent, self.handle_check_gmail)

        intent = IntentBuilder('GetLastGmailIntent')\
            .require('GetKeyword') \
	    .require('LastKeyword') \
            .require('GMailKeyword') \
            .build()
        self.register_intent(intent, self.handle_last_gmail)

        intent = IntentBuilder('GetXGmailIntent')\
            .require('GetKeyword') \
	    .require('LastKeyword') \
	    .require('XMailsKeyword') \
            .require('GMailKeyword') \
            .build()
        self.register_intent(intent, self.handle_x_gmail)

        intent = IntentBuilder('GetGmailIntent')\
            .require('GetKeyword') \
            .require('GMailKeyword') \
            .build()
        self.register_intent(intent, self.handle_gmail)


    def handle_check_gmail(self, message):
    	if not loggedIn():
    		self.speak_dialog('NotAccess')
    		return

    	self.speak_dialog("VerifyGMail")
    	email = main(max_results)
    	email = len(email)

    	if email > 0:
    		data = {"mails": email}
    		self.speak_dialog("ResultGmailsUnread",data)
    	else:
    		self.speak_dialog("NoEmails")


    def handle_last_gmail(self, message):
    	if not loggedIn():
    		self.speak_dialog('NotAccess')
    		return

    	description = message.data.get("utterance")

    	detail = False
    	if ("complete" in description) or ("full" in description) or ("detail" in description) or ("detailed" in description) or ("body" in description) :
    		detail = True

    	self.speak_dialog("VerifyGMail")
    	email = main(max_results)

    	if len(email) > 0:
    		self.GetMails(email,1,detail)
    	else:
    		self.speak_dialog("NoEmails")


    def handle_x_gmail(self, message):
    	if not loggedIn():
    		self.speak_dialog('NotAccess')
    		return

    	x_mails	= message.data.get("XMailsKeyword")
    	x_mails = int(x_mails)
    	description = message.data.get("utterance")

    	detail = False
    	if ("complete" in description) or ("full" in description) or ("detail" in description) or ("detailed" in description) or ("body" in description) :
    		detail = True

    	self.speak_dialog("VerifyGMail")
    	email = main(max_results)

    	if len(email) > 0:
    		data = {"mails": len(email),"read":x_mails}
    		self.speak_dialog("ResultGmails",data)
    		self.GetMails(email,x_mails,detail)
    	else:
    		self.speak_dialog("NoEmails")


    def handle_gmail(self, message):
    	if not loggedIn():
    		self.speak_dialog('NotAccess')
    		return

    	description = message.data.get("utterance")

    	detail = False
    	if ("complete" in description) or ("full" in description) or ("detail" in description) or ("detailed" in description) or ("body" in description) :
    		detail = True

    	self.speak_dialog("VerifyGMail")
    	email = main(max_results)

    	if len(email) > 0:
    		data = {"mails": len(email)}
    		self.speak_dialog("ResultGmailsMaximum",data)
    		self.GetMails(email,max_results,detail)
    	else:
    		self.speak_dialog("NoEmails")


def create_skill():
    return GoogleGmailSkill()
