import vk
import requests
import os
import urllib.request
import re


def url_exists(url):
    from urllib.request import urlopen
    try:
        ret = urlopen(url)
        return ret.code == 200
    except:
        return None


def delete_file(file):
    os.remove(file)


class VKPublic:

    def __init__(self, vk_api, public_id):
        self.vk_api = vk_api
        self.public_id = public_id

    def get_suggests(self):
        return self.vk_api.wall.get(owner_id=self.public_id, filter='suggests')

    def post_suggest(self, post_id):
        self.vk_api.wall.post(owner_id=self.public_id, post_id=post_id)

    def post(self, message):
        return self.vk_api.wall.post(owner_id=self.public_id, message=message)['post_id']

    def post(self, message, attachments):
        return self.vk_api.wall.post(owner_id=self.public_id, message=message, attachments=attachments)['post_id']

    def post(self, message, attachments, lat, long):
        return self.vk_api.wall.post(owner_id=self.public_id, message=message,
                                     attachments=attachments, lat=lat, long=long)['post_id']

    def delete(self, post_id):
        self.vk_api.wall.delete(owner_id=self.public_id, post_id=post_id)

    def edit(self, post_id, message):
        self.vk_api.wall.edit(owner_id=self.public_id, post_id=post_id, message=message)

    def edit(self, post_id, message, attachments):
        self.vk_api.wall.edit(owner_id=self.public_id,
                              post_id=post_id,
                              message=message,
                              attachments=attachments)

    def edit(self, post_id, message, attachments, lat, long):
        self.vk_api.wall.edit(owner_id=self.public_id,
                              post_id=post_id,
                              message=message,
                              attachments=attachments, lat=lat, long=long)

    @staticmethod
    def _replace_non_ascii(x):
        return ''.join(i if ord(i) < 128 else '_' for i in x)

    def get_photo_attachment(self, path_to_file, lat=None, lon=None):
        upload_url = self.vk_api.photos.getWallUploadServer(
            group_id=(-1) * int(self.public_id))['upload_url']
        if url_exists(path_to_file):
            urllib.request.urlretrieve(path_to_file, 'stream.jpg')
            filename_path = os.path.abspath('./stream.jpg')
            files = {'photo': (self._replace_non_ascii(os.path.basename(filename_path)),
                               open('./stream.jpg', 'rb'))}
        else:
            files = {'photo': (self._replace_non_ascii(os.path.basename(path_to_file)),
                               open(path_to_file, 'rb'))}
        post_response = requests.post(upload_url, files=files)
        photo_response = self.vk_api.photos\
            .saveWallPhoto(group_id=(-1) * int(self.public_id),
                           server=post_response.json()['server'],
                           photo=post_response.json()['photo'],
                           hash=post_response.json()['hash'],
                           latitude=lat, longitude=lon)
        photo_attachment = str(photo_response[0][u'id'])
        return photo_attachment

    def set_photo_attachment_location(self, photo_attachment, lon, lat):
        _, owner_id, photo_id = re.split('photo|_', photo_attachment)
        self.vk_api.photos.edit(owner_id=owner_id,
                                photo_id=photo_id,
                                latitude=lat,
                                longitude=lon)

    def get_audio_attachment(self, query):
        audio_response = self.vk_api.audio.search(q=query, auto_complete=1, count=1, sort=2)
        audio_attachment = 'audio' + str(audio_response[1][u'owner_id']) +\
                           '_' + str(audio_response[1][u'aid'])
        return audio_attachment

    def publish_suggests(self):
        suggested_posts = self.get_suggests()
        suggested_posts_count = suggested_posts[0]
        suggested_posts_ids = [post['id']
                               for post in suggested_posts[1:suggested_posts_count+1]
                               if post['post_type'] == 'suggest']
        for post_id in suggested_posts_ids:
            try:
                self.post_suggest(post_id)
            except Exception as e:
                print(e)
        return suggested_posts_count

