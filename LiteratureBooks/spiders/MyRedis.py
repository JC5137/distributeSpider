from scrapy.conf import settings
import redis

def get_redis():
    redis_args = dict(
        host=settings['REDIS_HOST'],
        port=settings['REDIS_PORT'],
    )
    return redis.Redis(**redis_args)
        
if __name__ == '__main__':
    redis_amzon = get_redis()