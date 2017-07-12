from scrapy.conf import settings
import redis

def get_redis():
    redis_args = dict(
        host=settings['MYREDIS_HOST'],
        port=settings['MYREDIS_PORT'],
        password=settings["MYREDIS_PASSWORD"]
    )
    return redis.Redis(**redis_args)
        
if __name__ == '__main__':
    my_redis = get_redis()
    print my_redis.keys()
    my_redis.lpush("AmzonSpider:start_urls","https://www.amazon.cn/s/ref=lp_658394051_il_ti_stripbooks?rh=n%3A658390051%2Cn%3A%21658391051%2Cn%3A658394051&ie=UTF8&qid=1497404708&lo=stripbooks")
    
