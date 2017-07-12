# -*- coding: utf-8 -*-

from LiteratureBooks.items import JdBooksItem
from LiteratureBooks.spiders.MyRedis import *
from LiteratureBooks.spiders.Bloomfilter import *
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
import logging
import re
import sys
import urllib
reload(sys)
sys.setdefaultencoding('utf8')



class JdSpider(RedisCrawlSpider):
    """Spider that reads urls from redis queue (JdSlaver:start_urls)."""
    name = 'JdSlaver'
    redis_key = 'JdSlaver:start_urls'
    
    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(JdSpider, self).__init__(*args, **kwargs)
        self.redis_server = get_redis()
        self.my_logger = logging.getLogger("JdSlaver")
    
    #根据亚马逊图书数据，搜索京东自营商品，采集价格、评论数、url入库
    def parse(self, response):
        book_name = urllib.unquote(re.findall("(?<=Search\?keyword=).+?(?=\&)",response.url)[0])
        book_id_amzon = re.findall("(?<=\&\|).+",response.url)[0]
        search_result = response.xpath("//meta[@name='description']/@content").extract()[0]
        search_result_num = int(re.findall(u"(?<=在京东找到了)[0-9]+(?=件)",search_result)[0])
        search_key = response.xpath("//strong[@class='search-key']").extract()
        if search_result_num != 0 or (not not search_key):
            try:
                item = JdBooksItem()
                item["book_name"] = book_name
                item["book_id_amzon"] = book_id_amzon
                books = response.xpath("//div[@id='J_goodsList']")
                book_price_measure_sheet = books.xpath("//div[@class='p-price']/strong/em/text()").extract()
                book_price_jd = books.xpath("//div[@class='p-price']/strong/i/text()").extract()
                book_url_jd = books.xpath("//div[@class='p-name']/a/@href").extract()
                book_comments_num_jd = books.xpath("//div[@class='p-commit']/strong/a/text()").extract()
                item["book_url_jd"] = re.findall(".+(?=\?)",book_url_jd[0].encode('utf-8'))[0]
                item["book_price_jd"] = book_price_measure_sheet[0].encode('utf-8') + book_price_jd[0].encode('utf-8') #
                item["book_comments_num_jd"] = self.comments_str_to_int(book_comments_num_jd)
                if not not re.search("//item.jd.com/[0-9]+\.html",item["book_url_jd"]):
                    yield item
            except Exception,e:
                self.my_logger.error(str(e))
                self.my_logger.error(response.url)
    
    #字符串类型的comments转为int
    def comments_str_to_int(self, comment_num_list):
        comment_num_str = comment_num_list[0].replace("+","")
        if "万" in comment_num_str:
            float_num = comment_num_str.replace("万","")
            return int(float(float_num) * 10000)
        else:
            return int(comment_num_str)