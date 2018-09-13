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
	'login' : ''
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

queryString = listToQueryParams(subscriptions, 'id')

print(queryString)

# TODO: this endpoint accepts max 100 IDs or Logins, split and do more requests
r = requests.get(twitchNewAPIEndpoint + '/users' + queryString,
				 headers=authHeaders)

response = r.json()

print(response)

# Build an [{display_name, id}] array of subscribed streamers

subscriptions = []
for element in response['data']:
	subscriptions.append({'display_name': element['display_name'],
						  'id': element['id']})