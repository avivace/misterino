import requests
import secrets
import json
"""
Twitch New API library
"""


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
            print('Something went wrong requesting the OAuth token ' +
                  repr(error))

        self.accessToken = response["access_token"]
        self.authHeaders = {'Authorization': 'Bearer ' + self.accessToken}

    """
    Get User info
    Given a loginName, or a list of them, return an object (or a list of objects)
    describing the given Users
    """

    def getUser(self, loginName):

        if type(loginName) is str:
            if not loginName.isdigit():
                payload = {'login': loginName}
            else:
                payload = {'id': loginName}

            r = requests.get(
                self.twitchNewAPIEndpoint + '/users',
                headers=self.authHeaders,
                params=payload)

            response = r.json()
            # TODO: Catch status != 200
            # Return the the first user requested
            return response["data"][0]

        elif type(loginName) is list:

            # We can't create dictionaries with duplicate key names, and the /users
            # endpoint wants ?login=user1&?login=user2&..9. for lists.
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

            if loginName[0].isdigit():
                queryString = listToQueryParams(loginName, 'id')
            else:
                queryString = listToQueryParams(loginName, 'login')

            # TODO: move this logic to getUserID
            # TODO: this endpoint accepts max 100 IDs or Logins, split and do more requests
            r = requests.get(
                self.twitchNewAPIEndpoint + '/users' + queryString,
                headers=self.authHeaders)

            response = r.json()
            return response["data"]

    """
    Get User ID
    """

    def getUserID(self, loginName):
        # TODO: should be able to accept an array of loginNames
        user = self.getUser(loginName)
        return user["id"]

    """
    Get User follows
    """

    def getUserFollows(self, userID):
        if not userID.isdigit():
            userID = self.getUserID(userID)

        payload = {'from_id': userID}

        r = requests.get(
            self.twitchNewAPIEndpoint + '/users/follows',
            headers=self.authHeaders,
            params=payload)

        response = r.json()

        totalSubs = response["total"]

        subscriptionsIDs = []
        for subscribedUser in response["data"]:
            subscriptionsIDs.append(subscribedUser["to_id"])

        ### Get more details on the list of followed users

        return self.getUser(subscriptionsIDs)
        # return subscriptionsIDs

    """
    Sets up Twitch webhooks (Phase 1)
    Subscribe/Unsubscribe to events
    """

    def updateWh(self, mode, userID):
        if not userID.isdigit():
            userID = self.getUserID(userID)

        secret = secrets.token_urlsafe(16)
        topic = 'https://api.twitch.tv/helix/streams?user_id=' + userID
        payload = {
            'hub.callback': self.config["TwitchCallback"] + ':3000/tw-webhook',
            'hub.mode': mode,
            'hub.topic': topic,
            'hub.lease_seconds': 60,
            'hub.secret': secret
        }
        r = requests.post(
            self.twitchNewAPIEndpoint + '/webhooks/hub',
            headers=self.authHeaders,
            params=payload)

        ## At this point, Twitch validates or not the request
        ## In the first case, it sends a challenge token to the specified callback
        return r

    def listWebhooks(self):
        r = requests.get(
            self.twitchNewAPIEndpoint + '/webhooks/subscriptions',
            headers=self.authHeaders)
        return r.json()
