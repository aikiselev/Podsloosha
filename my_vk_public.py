import vk
from vk_public import VKPublic
from os import environ

# public_id = '-101534490'
public_id = '-118729864' # mi_nerva
vksession = vk.AuthSession(user_login=environ.get("VK_EMAIL"),
                           user_password=environ.get("VK_PASS"),
                           app_id='5244211',
                           scope='wall,photos,offline')
vkapi = vk.API(vksession, lang='ru')
vkpublic = VKPublic(vkapi, public_id)

def main():
    print("Posted suggests: {}".format(vkpublic.publish_suggests()))

if __name__ == '__main__':
    main()
