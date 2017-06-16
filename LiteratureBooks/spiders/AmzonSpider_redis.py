from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from LiteratureBooks.spiders import MyRedis
from LiteratureBooks.spiders.MyRedis import *
import random



class AmzonSpider(RedisCrawlSpider):
    """Spider that reads urls from redis queue (AmzonSpider:start_urls)."""
    name = 'AmzonMaster'
    redis_key = 'AmzonSpider:start_urls'
    
    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(AmzonSpider, self).__init__(*args, **kwargs)
        self.redis_server = get_redis()
        self.website_domin = "https://www.amazon.cn"

    def parse(self, response):
        classfication_link = response.xpath("//div[@class='left_nav browseBox']/ul[2]/li/a/@href").extract()
        for link in self.get_link(classfication_link[0:2]):
            self.redis_server.lpush('AmzonSlaver:start_urls',self.website_domin + link)          
    def get_link(self,linkset):
        for link in linkset:
            yield link