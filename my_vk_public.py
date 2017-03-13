import vk
from vk_public import VKPublic
from os import environ

public_id = '-101534490' # posloosha.periscope
vksession = vk.Session(access_token=environ.get("VK_ACCESS_TOKEN"))
vkapi = vk.API(vksession, lang='ru')
vkpublic = VKPublic(vkapi, public_id)


def main():
    print(f"Posted suggests: {vkpublic.publish_suggests()}")

if __name__ == '__main__':
    main()
