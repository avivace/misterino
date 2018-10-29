import requests
import json

from config import loadConfig

class twitch():

	def __init__(self, config):
		self.twitchOAuthEndpoint = 'https://id.twitch.tv/oauth2/token'
		self.twitchNewAPIEndpoint = 'https://api.twitch.tv/helix'
		self.config = config
		self.updateToken()

	"""
	Get OAuth Token
	OAuth Client Credentials Flow (server-server)
	"""
	def updateToken(self):
		payload = {
			'client_id': self.config["TwitchAppClientID"],
			'client_secret': self.config["TwitchAppClientSecret"],
			'grant_type': 'client_credentials'
		}

		try:
			r = requests.post(self.twitchOAuthEndpoint, params=payload)
			response = r.json()
			r.raise_for_status()
		except Exception as error:
			print('Something went wrong requesting the OAuth token ' + repr(error))

		self.accessToken = response["access_token"]
		self.authHeaders = {
			'Authorization': 'Bearer '+self.accessToken
		}

	"""
	Get User info
	"""
	def getUser(self, loginName): 
		payload = {
			'login' : loginName
		}

		r = requests.get(self.twitchNewAPIEndpoint + '/users',
						 headers=self.authHeaders,
						 params=payload)

		response = r.json()
		# TODO: Catch status != 200
		# Return the the first user requested
		return response["data"][0]
	
	"""
	Get User ID
	"""
	def getUserID(self, loginName):
		user = self.getUser(loginName)
		return user["id"]






config = loadConfig()
twitch = twitch(config)
print(twitch.getUserID("darkpuma"))