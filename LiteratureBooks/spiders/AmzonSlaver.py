#coding:utf-8

from LiteratureBooks.items import LiteraturebooksItem
from LiteratureBooks.spiders.MyRedis import *
from LiteratureBooks.spiders.Bloomfilter import *
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy import Request
import logging
import sys
import re
reload(sys)
sys.setdefaultencoding('utf8')

class AmzonSpider(RedisCrawlSpider):
    """Spider that reads urls from redis queue (AmzonSlaver:start_urls)."""
    name = 'AmzonSlaver'
    redis_key = 'AmzonSlaver:start_urls'
    
    def __init__(self, *args, **kwargs):
        # Dynamically define the allowed domains list.
        domain = kwargs.pop('domain', '')
        self.allowed_domains = filter(None, domain.split(','))
        super(AmzonSpider, self).__init__(*args, **kwargs)
        
        self.amzon_website_domin = "https://www.amazon.cn"
        self.jd_search = "https://search.jd.com/Search?keyword=%s&enc=utf-8&wtype=1&click=1"
        self.redis_server = get_redis()
        #采用布隆过滤器进行数据判重，也可根据redis_set判重，看数据量大小
        self.amzon_bloomfilter = BloomFilter(key = 'amzon_bloomfilter')
        self.jd_bloomfilter = BloomFilter(key = 'jd_bloomfilter')
        self.my_logger = logging.getLogger("AmzonSlaver")
        
    #解析数据
    def parse(self, response):
        #解析页码
        page_num = 1
        parse_page_num = re.findall("(?<=\&page=)[0-9]+",response.url)
        if parse_page_num != []:
            page_num = int(parse_page_num[0])
        
        #计算起始数据编号与结束数据编号
        result_count = int(response.xpath("//h2[@id='s-result-count']/text()").re("(?<=\-)[0-9]+")[0])
        result_start = (page_num - 1) * 60
        if result_start > result_count:
            return
        
        #数据解析，遍历整个结果页，获取图书url、图书ID、图书名称、评论数、价格区间（注:需求无说明采集图书哪种价格）
        for result_id in xrange(result_start,result_count):
            try:
                item = LiteraturebooksItem()
                book = response.xpath("//li[@id='result_%d']" % result_id)
                book_url_amzon = book.xpath("div/div/div[1]/a[@class = 'a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal']/@href").extract()
                book_name = book.xpath("div/div/div[1]/a/h2/text()").extract()
                book_price_amzon = book.xpath("div/div[@class = 'a-row a-spacing-none']/div[@class='a-row a-spacing-none']/a/span/text()").extract()
                book_comments_num_amzon = book.xpath("div[@class='s-item-container']/div[@class='a-row a-spacing-none']/div[@class='a-row a-spacing-top-mini a-spacing-none']/a/text()").extract()
                
                #进行链接标准化,提取Url中图书名称与分类号组成的链接
                item["book_url_amzon"] = re.findall(".+(?=\/ref)",book_url_amzon[0].encode('utf-8'))[0]
                item["book_id_amzon"]  = re.findall("(?<=\/dp\/).+",item["book_url_amzon"])[0]
                item["book_name"] = book_name[0].encode('utf-8') if book_name != [] else ''
                item["book_comments_num_amzon"] = int(book_comments_num_amzon[0].encode('utf-8').replace(',','')) if book_comments_num_amzon != [] else 0
                item["book_price_amzon"] = ''.join(book_price_amzon).encode('utf-8')
                
                #如果价格发生变化,更新数据,或者没有采集过,插入数据库
                amzon_finger_print = item["book_url_amzon"]+item["book_price_amzon"]
                if not self.amzon_bloomfilter.is_contains(amzon_finger_print):
                    yield item
                    self.amzon_bloomfilter.insert(amzon_finger_print)
                
                #链接去重,如果没有采集，加到JdSlaver队列
                jd_finger_print = item["book_name"] + item["book_id_amzon"]
                if not self.jd_bloomfilter.is_contains(jd_finger_print):
                    self.jd_bloomfilter.insert(jd_finger_print)
                    self.redis_server.lpush('JdSlaver:start_urls', self.jd_search %  item["book_name"] + "&|" +item["book_id_amzon"])
            
            except Exception,e:
                self.my_logger.error(str(e))
                self.my_logger.error(response.url)
                self.my_logger.error(str(result_id))
        
        #获取下一页，然后递归采集直至下一页为空
        next_page = response.xpath("//a[@id='pagnNextLink']/@href").extract()
        if next_page != []:
            yield Request(self.amzon_website_domin + next_page[0], callback=self.parse)