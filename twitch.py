import requests
import json

from config import loadConfig

# TODO: pass config or run standalone?
config = loadConfig()


twitchOAuthEndpoint = 'https://id.twitch.tv/oauth2/token'
twitchNewAPIEndpoint = 'https://api.twitch.tv/helix'

### Get OAuth Token
#  OAuth Client Credentials Flow (server-server)

payload = {
	'client_id':config["TwitchAppClientID"],
	'client_secret':config["TwitchAppClientSecret"],
	'grant_type': 'client_credentials'
}

r = requests.post(twitchOAuthEndpoint, params=payload)
response = r.json()
# TODO: Catch status != 200

accessToken = response["access_token"]

authHeaders = {
	'Authorization': 'Bearer '+accessToken
}

### Get User ID of a given login name
payload = {
	'login' : 'darkpuma'
}

r = requests.get(twitchNewAPIEndpoint + '/users',
				 headers=authHeaders,
				 params=payload)

response = r.json()
# TODO: Catch status != 200

# Extract the id of the first user requested
userID = response["data"][0]["id"]

### Get User follows
payload = {
	'from_id' : userID
}

r = requests.get(twitchNewAPIEndpoint + '/users/follows',
				 headers=authHeaders,
				 params=payload)

response = r.json()

totalSubs = response["total"]

subscriptions = []
for subscribedUser in response["data"]:
	subscriptions.push(subscribedUser["to_id"])

