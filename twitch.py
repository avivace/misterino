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

	"""
	Get User follows
	"""
	def getUserFollows(self, userID):
		payload = {
			'from_id' : userID
		}

		r = requests.get(self.twitchNewAPIEndpoint + '/users/follows',
						 headers=self.authHeaders,
						 params=payload)

		response = r.json()

		totalSubs = response["total"]

		subscriptionsIDs = []
		for subscribedUser in response["data"]:
			subscriptionsIDs.append(subscribedUser["to_id"])

		### Get more details on the list of followed users

		# We can't create dictionaries with duplicate key names, and the /users 
		# endpoint wants ?login=user1&?login=user2&... for lists. 
		# So, enjoy this abomination or waste hundreds of API calls and get ratelimited

		def listToQueryParams(array, param):
			queryString = ''

			for element in array:
				if element == array[0]:
					queryString += '?'
				else:
					queryString += '&'
				queryString += param + '=' + element

			return queryString

		queryString = listToQueryParams(subscriptionsIDs, 'id')

		print(queryString)

		# TODO: this endpoint accepts max 100 IDs or Logins, split and do more requests
		r = requests.get(self.twitchNewAPIEndpoint + '/users' + queryString,
						 headers=self.authHeaders)

		response = r.json()

		return response["data"]





config = loadConfig()
twitch = twitch(config)
userID = twitch.getUserID("darkpuma")
print(twitch.getUserFollows(userID))