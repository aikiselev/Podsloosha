#!/usr/bin/env python3
# -*- coding: utf8 -*-
from my_vk_public import *
from periscope_api import PeriscopeAPI
from math import log1p
import polling
from dateutil import parser, tz
from datetime import datetime
from simplekv.fs import FilesystemStore
import json
from daemonize import Daemonize
import logging

import locale
locale.setlocale(locale.LC_ALL, "ru_RU.utf8")


class Location:

    def __init__(self, p1_lat, p1_lon, p2_lat, p2_lon):
        self.p1_lat = p1_lat
        self.p1_lon = p1_lon
        self.p2_lat = p2_lat
        self.p2_lon = p2_lon

    def get_streams(self, include_replay=False):
        periscope_api = PeriscopeAPI()
        return periscope_api.mapGeoBroadcastFeed(self.p1_lat, self.p1_lon, self.p2_lat, self.p2_lon,
                                                 include_replay=include_replay)


def get_stream_rating(broadcast_id):
    periscope_api = PeriscopeAPI()
    users = periscope_api.getBroadcastUsers(broadcast_id)

    rating = 0
    for user in users['live']:
        rating += log1p(user['n_followers']) * (1 + 0.05 * user['n_hearts_given'])
    for user in users['replay']:
        rating += log1p(user['n_followers']) * (1 + 0.05 * user['n_hearts_given']) * 0.6
    rating += 0.1 * users['n_web_watched']
    return round(rating)


def get_stream_info(broadcast_id):
    periscope_api = PeriscopeAPI()
    stream = periscope_api.getBroadcasts([broadcast_id])
    if stream is not None and not 'msg' in stream:
        return stream


def get_streams_info(broadcast_ids):
    if not broadcast_ids:
        return []
    periscope_api = PeriscopeAPI()
    streams = periscope_api.getBroadcasts(broadcast_ids)
    if streams is not None and 'msg' not in streams:
        return streams


class PeriscopeAdvertiser:

    def __init__(self, _locations, _db, _logger=logging.getLogger()):
        self.db = _db  # {'stream_id': {'post_id', 'state'}}
        self.locations = _locations
        self.logger = _logger

    @staticmethod
    def _parse_time(time_string):
        local_tz = tz.tzlocal()
        return parser.parse(time_string).astimezone(local_tz).strftime("%H:%M, %d %B")

    @staticmethod
    def state_description(stream):
        state = stream['state']
        if state == "ENDED":
            return """Запись ({time})""".format(
                time="От " + PeriscopeAdvertiser._parse_time(stream['end']))
        elif state == "RUNNING":
            return "Прямой эфир"
        elif state == "TIMED_OUT":
            return """Эфир прерван ({time})""".format(
                time="Был начат в " + PeriscopeAdvertiser._parse_time(stream['created_at']))
        else:
            return "Статус недоступен"

    @staticmethod
    def get_advertisement(stream):
        return """Название: {status} | {state_description}
        Автор: {name}
        В приложении: pscp://broadcast/{id}
        На сайте: https://periscope.tv/{username}/{id}""".format(
            state_description=PeriscopeAdvertiser.state_description(stream),
            status=stream['status'],
            name=stream['user_display_name'],
            id=stream['id'],
            username=stream['username'])

    @staticmethod
    def get_image(stream):
        return stream['image_url']

    @staticmethod
    def get_location(stream):
        return {
            'lat': stream['ip_lat'],
            'lon': stream['ip_lng']
        }

    @staticmethod
    def prepare_post(stream):
        advertisement = PeriscopeAdvertiser.get_advertisement(stream)
        link = "https://periscope.tv/{username}/{id}".format(
            id=stream['id'],
            username=stream['username'])
        photo_url = PeriscopeAdvertiser.get_image(stream)
        location = PeriscopeAdvertiser.get_location(stream)
        photo_attach = vkpublic.get_photo_attachment(photo_url,
                                                     lon=location['lon'],
                                                     lat=location['lat'])
        return {'message': advertisement,
                'attachments': ','.join([link, photo_attach]),
                'long': location['lon'], 'lat': location['lat']}

    def db_put(self, key, value):
        return self.db.put(key, json.dumps(value).encode(encoding='UTF-8'))

    def db_get(self, key):
        return json.loads(self.db.get(key).decode(encoding='UTF-8'))

    def edit_stream(self, stream):
        post = self.prepare_post(stream)
        post_id = self.db_get(stream['id'])['post_id']
        try:
            vkpublic.edit(post_id, post['message'], attachments=post['attachments'],
                          long=post['long'], lat=post['lat'])
            self.db_put(stream['id'], {'post_id': post_id, 'state': stream['state']})
        except Exception as e:
            self.logger.warn(e)

    def post_stream(self, stream):
        post = self.prepare_post(stream)
        try:
            post_id = vkpublic.post(post['message'], attachments=post['attachments'],
                                    long=post['long'], lat=post['lat'])
            self.db_put(stream['id'], {'post_id': post_id, 'state': stream['state']})
        except Exception as e:
            self.logger.warn(e)

    def delete_stream(self, stream_id):
        vkpublic.delete(self.db_get(stream_id)['post_id'])
        self.db.delete(stream_id)

    def poll(self):
        self.logger.info("••••• Poll started: {start_time} •••••".format(
            start_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        # check for deletion of old streams
        db_keys = self.db.keys()
        streams_info = dict((s['id'], s) for s in get_streams_info(db_keys))
        for stream_id in db_keys:
            if stream_id not in streams_info:
                self.logger.info("Deleting stream: " + stream_id)
                self.delete_stream(stream_id)
            else:
                new_state = streams_info[stream_id]['state']
                old_state = self.db_get(stream_id)['state']
                if new_state != old_state:
                    self.logger.info("Changing state: {id} | {old} -> {new}".format(
                        id=stream_id, old=old_state, new=new_state))
                    self.edit_stream(streams_info[stream_id])
        # add new streams
        streams = []
        for location in self.locations:
            streams += location.get_streams(include_replay=True)
        for stream in streams:
            if stream['id'] not in db_keys:
                self.logger.info("Adding stream: " + stream['id'])
                self.post_stream(stream)
        self.logger.info("••••• Poll ended: {end_time} •••••".format(
            end_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")))


def main(logger):
    def main():
        db = FilesystemStore("/home/kiselev/db")
        poll_cooldown = 30
        locations = [Location(56.880372, 60.729744, 56.928178, 60.843899)]
        advertiser = PeriscopeAdvertiser(locations, db, logger)
        polling.poll(advertiser.poll, step=poll_cooldown, poll_forever=True)
    return main

if __name__ == '__main__':
    pid = "/tmp/podsloosha.pid"
    logging.basicConfig(filename='/tmp/podsloosha.log',level=logging.DEBUG)
    logging.getLogger("requests").setLevel(logging.ERROR)
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    daemon = Daemonize(app="Podsloosha", pid=pid, action=main(logger))
    daemon.start()

