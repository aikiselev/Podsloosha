import logging

from celery import Celery, task
from datetime import timedelta
from os import environ
from periscope_streams import PeriscopeAdvertiser, Location
from simplekv.db.mongo import MongoStore
import pymongo


# Fetch the Redis connection string from the env, or use localhost by default
REDIS_URL = environ.get('REDISTOGO_URL', 'redis://localhost')

# Setup the celery instance under the 'tasks' namespace
app = Celery('tasks')

# Use Redis as our broker and define json as the default serializer
app.conf.update(
    BROKER_URL=REDIS_URL,
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERYBEAT_SCHEDULE = {
        'poll-podsloosha': {
            'task': 'tasks.poll_podsloosha',
            'schedule': timedelta(seconds=10)
        },
    }
)

locations = [Location(56.880372, 60.729744, 56.928178, 60.843899)]
# db = RedisStore(redis.from_url(REDIS_URL))
mongo_client = pymongo.MongoClient(environ.get('MONGODB_URI', 'mongodb://localhost'))
mongo_db = mongo_client.get_default_database()
db = MongoStore(mongo_db, 'streams')

@task
def poll_podsloosha():
    advertiser = PeriscopeAdvertiser(locations, db)
    advertiser.poll()


# # Define the fibonacci function for use in our task
# def fib(n):
#     if n > 1:
#         return fib(n - 1) + fib(n - 2)
#     else:
#         return 1

# # The periodic task itself, defined by the following decorator
# @task
# def print_fib():
#     # Just log fibonacci(30), no more
#     logging.info(fib(30))
