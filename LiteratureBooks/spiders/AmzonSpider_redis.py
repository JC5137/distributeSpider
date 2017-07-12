#coding:utf-8
import random
from LiteratureBooks.spiders import MyRedis
from LiteratureBooks.spiders.MyRedis import *
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy import Request


class AmzonSpider(RedisCrawlSpider):
    """Spider that reads urls from redis queue (AmzonSpider:start_urls)."""
    name = 'AmzonMaster'
    redis_key = 'AmzonSpider:start_urls'
    
    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(AmzonSpider, self).__init__(*args, **kwargs)
        print args
        print kwargs
        self.redis_server = get_redis()
        self.amzon_website_domin = "https://www.amazon.cn"
    
    #解析文学图书所有分类url
    def parse(self, response):
        classfication_link = response.xpath("//div[@class='left_nav browseBox']/ul[2]/li/a/@href").extract()
        for link in classfication_link:
            yield Request(self.amzon_website_domin + link,callback=self.parse_url)
    
    #获取图像视图,解析url进入AmzonSlaver队列
    def parse_url(self, response):
        image_view = u'图像视图'
        image_url = response.xpath(u"//a[@title='%s']/@href" %image_view).extract()
        if image_url != []:
            self.redis_server.lpush('AmzonSlaver:start_urls',self.amzon_website_domin + image_url[0])