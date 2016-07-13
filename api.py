import requests
import json
import os

import friend as friendo

SECRETS_FILENAME = "SECRETS.json"


class AuthenticationError(Exception):
    """Yeah it's really important to write extremely enterprise well-documented hacky API code. Hacker News will love it I swear."""


class NSASimulator:

    BASE_URL = "https://api.gotinder.com/"

    def __init__(self, facebook_auth_filename):
        self.headers = {
            "User-Agent": "Tinder Android Version 5.2.0",
            "Accept-Language": "en",
            "host": "api.gotinder.com",
            "Conection": "Keep-Alive",
            "If-None-Match": 'W/"1630244057"',
            "app-version": 1546,
            "os-version": 23,
            "platforms": "android"
        }
        self._load_fb_auth()
        self._auth()
        self.friends = set()


    def _load_fb_auth(self):
        if os.path.exists(SECRETS_FILENAME) and os.path.isfile(SECRETS_FILENAME):
                with open(SECRETS_FILENAME) as f:
                    self.fb_auth = json.load(f)
        else:
            raise AuthenticationError("Couldn't find {secrets_filename}. Did you create it and put your Facebook user id and auth token in it?".format(secrets_filename=SECRETS_FILENAME))

    def _auth(self):
        """
        You can only log in to Tinder with Facebook.

        This logs into Tinder with your supplied Facebook id and token,
        gets you a Tinder auth token which we're going to need for all our future API requests.

        This is only going to work if you already have a Tinder account
        connected to your Facebook account sorry fam.

        """
        response = requests.post(self.BASE_URL + "auth", data=self.fb_auth)
        if response.status_code == 200:
            self.headers["X-Auth-Token"] = response.json()["token"]
            print("Authenticated to Tinder 🔒🔥")
        else:
            raise AuthenticationError("Hey your Tinder auth didn't work. Did you put your Facebook user id and auth token into SECRETS.txt?")


    def _get(self, url):
        response = requests.get(self.BASE_URL + url, headers=self.headers)
        print(response.text)
        return response

    def get_facebook_friends_tinder_ids(self):
        friend_data = self._get("group/friends").json()
        for result in friend_data["results"]:
            # Alright it's time for this json "parsing" fiesta.
            name = result["name"]
            tinder_id = result["user_id"]
            photos = result["photo"]
            sample_photo = photos[0]["processedFiles"][0]

            # Just pick any url to extract the Facebook ID from.
            sample_url = sample_photo["url"]
            facebook_id = sample_url.split("/")[3]

            self.friends.add(friendo.Friend(name, facebook_id, tinder_id))

        return self.friends

    def get_profile(friend):
        profile_data = self._get("user/" + friend.tid).json()["results"]
        return profile_data

if __name__ == "__main__":
        stalker = NSASimulator(facebook_auth_filename="SECRETS.json")
