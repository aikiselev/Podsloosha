import requests

cookie = "WlUD93siVXNlcklkIjoiNDQwMyIsIlNlc3Npb24iOiI4MThnTC1RaWlvN3UwalRiWHl1T3J4MGhEYzd6OG9IUTB4WmxYc0NNMHhZIi" \
         "wiVmVyc2lvbiI6MX1CSk3C4AeHcA4aoKUDgpOPUaQkhQJFw7tLJ38iMfrAJg=="
# Periscope Consumer Key - 9I4iINIyd0R01qEPEwT9IC6RE
# Periscope Secret Key - BDP2fLhkfHdQ3TynI1mzOQyJAODtLCTPv2JHdcNSiYM2rUIsyG
# How to get another cookie: http://pmmlabs.ru/blog/2016/03/27/periscope-pc-client/

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
        else:
            return response

    def getBroadcastUsers(self, broadcast_id):
        url = self.api_url + "getBroadcastViewers"
        response = requests.post(url, json={
            'broadcast_id': broadcast_id,
            'cookie': cookie
        }, timeout=3)

        if response.status_code == 200:
            return response.json()
