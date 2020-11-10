from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from yeelight import discover_bulbs
from yeelight import Bulb
import dateutil.parser

#   Documentation / Installation :
#   ------------------------------
#   [needs python 3]
#
#   Yeelight installation
#   https://yeelight.readthedocs.io/en/latest/
#   - pip install yeelight
#   - Enable LAN Access using Yeelight App
#
#   Google Calendar API 
#   - pip install dateutils
#   - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
#   - follow instructions in : https://developers.google.com/calendar/quickstart/python
#   - Save credentials.json to the same folder.
#
#   Add Linux["Cron"] or 
#    Windows["Task Scheduler"->"Create Task"] : each 5 minutes.
#
#   Debugging : 
#   -----------
#   cd /user/in_meeting_light\ or  cd C:\Main\xampp_htdocs\in_meeting_light\
#   python in_meeting_light.py
#
#


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
COMPANY_DOMAIN = "@protected.media"
BULB_NAME = "Yeelight LED Color"

def in_meeting_logic(meeting_found,attendees_found,attendees_out_of_company_found):
	
	print ( "=== meeting_found=" , meeting_found , ",attendees_found=" , attendees_found , ",attendees_out_of_company_found=" , attendees_out_of_company_found )
	
	# red : 255,0,0 , pink : 255,105,180 , green : 0,128,0 , white : 255,255,255

	if attendees_out_of_company_found:
		bulb_light("on",255,0,0) 		# red

	elif attendees_found:
		bulb_light("on",0,128,0) 		# green

	elif meeting_found:
		bulb_light("off",0,0,0)

	else:
		bulb_light("off",0,0,0)


def bulb_light(status,r,g,b):	
	try:
		bulbs = discover_bulbs() # bulb.set_name("Yeelight LED Color")	
		print ("bulbs=",bulbs)
		for bulb in bulbs:
			if bulb['capabilities']['name'] == BULB_NAME:		
				power = bulb['capabilities']['power']
				found_bulb = Bulb(bulb['ip'])
				print ("found_bulb:",found_bulb)
				if status=="off":
					found_bulb.turn_off()
				elif status=="on":					
					if power=="off":
						found_bulb.turn_on()						
					found_bulb.set_rgb(r, g, b)					
	except:
		pass


def time_in_range(minutes_ahead,start_str,end_str):

	start = dateutil.parser.parse(start_str).replace(tzinfo=None)
	end = dateutil.parser.parse(end_str).replace(tzinfo=None)
		
	checked_time = datetime.datetime.now() + datetime.timedelta( minutes=minutes_ahead )

	if checked_time >=  start and checked_time <= end :
		return True
	else:
		return False

def main():
	"""Shows basic usage of the Google Calendar API.
	Prints the start and name of the next 10 events on the user's calendar.
	"""
	creds = None
	# The file token.pickle stores the user's access and refresh tokens, and is
	# created automatically when the authorization flow completes for the first
	# time.
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
			creds = flow.run_local_server(port=0)
		# Save the credentials for the next run
		with open('token.pickle', 'wb') as token:
			pickle.dump(creds, token)

	service = build('calendar', 'v3', credentials=creds)

	# Call the Calendar API , we assume that we don't have event that is longer than 6 hours
	# and we don't have more than 20 events in these 6 hours ..
	
	tmin = datetime.datetime.utcnow() - datetime.timedelta( hours = 6 )
	tmin_z = tmin.isoformat() + 'Z' # 'Z' indicates UTC time

	print('Getting the upcoming events...')
	events_result = service.events().list(	calendarId = 'primary', 
											timeMin = tmin_z,
											maxResults = 20, 
											singleEvents = True,
											orderBy = 'startTime').execute()
	events = events_result.get('items', [])

	if not events:
		print('No upcoming events found.')
		
	# ----------------------------------------------------------------
	# starting events analysis ...
	# can use print ( repr ( event['attendees'] )) for debugging ...
	# ----------------------------------------------------------------
	meeting_found = False
	attendees_found = False
	attendees_out_of_company_found = False
	
	for event in events:
		start = event['start'].get('dateTime', event['start'].get('date'))
		end = event['end'].get('dateTime', event['end'].get('date'))
		print ( "event:" , start , end , ",Summary:", event['summary'] )
		
		if not ( time_in_range(0,start,end) or time_in_range(10,start,end) ):
			continue
		meeting_found = True
		
		if 'attendees' in event.keys():
			attendees_found = True
			for attendee in event['attendees']:				
				email_without_company = attendee['email'].replace(COMPANY_DOMAIN, "")
				if "@" in email_without_company:					
					attendees_out_of_company_found = True					
			
	in_meeting_logic(meeting_found,attendees_found,attendees_out_of_company_found)
	# ----------------------------------------------------------------
	
if __name__ == '__main__':
	main()



