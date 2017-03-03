import requests
import json
import os
from pprint import pprint

from dateutil import parser
from datetime import timezone

import friend as friendo

SECRETS_FILENAME = "SECRETS.json"


class AuthenticationError(Exception):
    """Yeah it's really important to write extremely enterprise well-documented hacky API code. Hacker News will love it I swear."""

class MoralityException(Exception):
    """It might come in handy later."""

class SquadError(Exception):
    """I have no excuse for this one."""


class NSASimulator:

    BASE_URL = "https://api.gotinder.com/"

    def __init__(self, facebook_auth_filename=SECRETS_FILENAME):

        # Look I have no idea what these are I just copy/pasted
        # them from the API call my phone makes. If this makes
        # you uncomfortable then you probably chill dude it's just bytes.
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
        self.authed = False
        self.profiles = None
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
            self.authed = True
        else:
            raise AuthenticationError("Hey your Tinder auth didn't work. Did you put your Facebook user id and auth token into {secrets_filename}?".format(secrets_filename=SECRETS_FILENAME))

    def _post(self, url, data):
        if not self.authed:
            self._auth()
        response = requests.post(self.BASE_URL + url, headers=self.headers, data=data)
        print(response.text)
        return response

    def _get(self, url):
        if not self.authed:
            self._auth()
        print(self.headers)
        response = requests.get(self.BASE_URL + url, headers=self.headers)
        print(response.text)
        return response

    def get_facebook_friends_tinder_ids(self):

        if not os.path.exists(".creepyfile"):
            be_creepy = input("Sure you want to look at your Facebook friends' Tinder profiles? They might not like that. 🔒 [y/n]: ").lower() in ("y", "yes")

            if not be_creepy:
                raise MoralityException("😇 ")
            else:
                with open(".creepyfile", "w") as f:
                    f.write("😈")
                print("🔌🌐🔌")

        request = self._get("group/friends")
        if request.status_code != 200:
            raise SquadError("Couldn't get info about your friends. Is Tinder Social enabled on your account? Hint: If you're not in Australia it probably isn't.")

        friend_data = request.json()
        for result in friend_data["results"]:
            # Alright it's time for this json "parsing" fiesta.
            name = result["name"]
            tinder_id = result["user_id"]
            photos = result["photo"]
            sample_photo = photos[0]["processedFiles"][0]
            pprint(result)
            # Just pick any url to extract the Facebook ID from.
            sample_url = sample_photo["url"]
            facebook_id = sample_url.split("/")[3]

            self.friends.add(friendo.Friend(name, facebook_id, tinder_id))

        return self.friends

    def get_profile(self, friend):
        profile_data = self._get("user/" + friend.tid).json()["results"]

        # Let's just put some smooth UX on that.
        extra_datums = {
            "ping_time": self._to_local_time(profile_data["ping_time"]),
            "birth_date": self._to_local_time(profile_data["birth_date"]),
            "like_url": "like/?user=" + friend.tid,
            "superlike_url": "superlike/?user=" + friend.tid,
            "pass_url": "pass/?user=" + friend.tid
        }

        # I apologise for nothing.
        profile_data.update(extra_datums)

        return profile_data

    @staticmethod
    def _to_local_time(timestring):

        def utc_to_local(utc_dt):
            return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

        datetime_ = parser.parse(timestring)
        return utc_to_local(datetime_).strftime("%b %d %Y %H:%M:%S")

    def get_profiles(self):
        if self.profiles is not None:
            return self.profiles
        friends = self.get_facebook_friends_tinder_ids()
        self.profiles = [self.get_profile(friend) for friend in friends]
        self.profiles.sort(key=lambda p: p["name"])
        return self.profiles

    def like(self, user):
        print(user)
        print(self.BASE_URL + "like/" + user)
        self._get("like/" + user)

    def superlike(self, user):
        print(user)
        print(self.BASE_URL + "like/" + user + "/super")
        self._post("like/" + user + "/super", {})

    def pass_vote(self, user):
        print(user)
        print("here's the part where I make a request to {base_url}{url}".format(base_url=self.BASE_URL, url="pass/" + user))

if __name__ == "__main__":
        stalker = NSASimulator(facebook_auth_filename="SECRETS.json")
