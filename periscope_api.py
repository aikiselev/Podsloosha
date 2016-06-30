import requests

cookie = "WGkGYTFQWEVkd1JCeXJqZXZo5aBR3R3o_PzVqgZs7niLEeb_6jYo0XjaOhe-D9Fhag=="


class PeriscopeAPI():

    api_url = "https://api.periscope.tv/api/v2/"

    def getBroadcasts(self, broadcast_ids=[]):
        url = self.api_url + "getBroadcasts"
        response = requests.post(url, json={
            'broadcast_ids': broadcast_ids,
            'cookie': cookie
        }, timeout=3)

        if response.status_code == 200:
            return response.json()

    def mapGeoBroadcastFeed(self, p1_lat, p1_lng, p2_lat, p2_lng, include_replay=False):
        url = self.api_url + "mapGeoBroadcastFeed"
        response = requests.post(url, json={
            'p1_lat': p1_lat, 
            'p1_lng': p1_lng,
            'p2_lat': p2_lat,
            'p2_lng': p2_lng,
            'cookie': cookie,
            'include_replay': include_replay
        }, timeout=3)

        if response.status_code == 200:
            return response.json()

    def getBroadcastUsers(self, broadcast_id):
        url = self.api_url + "getBroadcastViewers"
        response = requests.post(url, json={
            'broadcast_id': broadcast_id,
            'cookie': cookie
        }, timeout=3)

        if response.status_code == 200:
            return response.json()
