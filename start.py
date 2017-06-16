import redis
amzon_redis = redis.Redis(host='127.0.0.1', port=6379,db=0)
amzon_redis.lpush("AmzonSpider:start_urls","https://www.amazon.cn/s/ref=lp_658394051_il_ti_stripbooks?rh=n%3A658390051%2Cn%3A%21658391051%2Cn%3A658394051&ie=UTF8&qid=1497404708&lo=stripbooks")