import logging

from celery import Celery, task
from datetime import timedelta
from os import environ
from periscope_streams import PeriscopeAdvertiser, Location
from simplekv.db.mongo import MongoStore
import pymongo

# Fetch the Redis connection string from the env, or use localhost by default
REDIS_URL = environ.get('REDIS_URL', 'redis://localhost')

# Setup the celery instance under the 'tasks' namespace
app = Celery('tasks')
app.conf.update(
    BROKER_URL=REDIS_URL,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERYBEAT_SCHEDULE={
        'poll-podsloosha': {
            'task': 'tasks.poll_podsloosha',
            'schedule': timedelta(seconds=15)
        },
    }
)

locations = [Location(56.880372, 60.729744,
                      56.928178, 60.843899)]
mongo_client = pymongo.MongoClient(environ.get('MONGODB_URI', 'mongodb://localhost'),
                                   connect=False)


@task
def poll_podsloosha():
    mongo_db = mongo_client.get_default_database()
    db = MongoStore(mongo_db, 'streams')
    advertiser = PeriscopeAdvertiser(locations, db)
    advertiser.poll()
