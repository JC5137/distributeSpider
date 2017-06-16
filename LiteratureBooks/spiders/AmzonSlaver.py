#coding:utf-8
from scrapy.spiders import Rule
from scrapy.linkextractors import LinkExtractor
from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.conf import settings
from LiteratureBooks.items import LiteraturebooksItem
import scrapy
import re
from LiteratureBooks.spiders.MyRedis import *
from LiteratureBooks.spiders.Bloomfilter import *
import sys
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
        self.bloomfilter = BloomFilter(key = 'amzon_bloomfilter')
    def parse(self, response):
        #获取图像视图,解析数据
        image_view = u'图像视图'
        image_url = response.xpath(u"//a[@title='%s']/@href" %image_view).extract()
        if image_url != []:
            yield scrapy.Request(self.amzon_website_domin + image_url[0], callback=self.parse_data)
    def parse_data(self, response):
        parse_page_num = re.findall("(?<=\&page=)[0-9]+",response.url)
        page_num = 1
        if parse_page_num != []:
            page_num = int(parse_page_num[0])
        for result_id in xrange((page_num - 1) * 60,page_num * 60):
            try:
                item = LiteraturebooksItem()
                book = response.xpath("//li[@id='result_%d']" % result_id)
                book_url_amzon = book.xpath("div/div/div[1]/a[@class = 'a-link-normal s-access-detail-page  s-color-twister-title-link a-text-normal']/@href").extract()
                book_name = book.xpath("div/div/div[1]/a/h2/text()").extract()
                book_price_amzon = book.xpath("div/div[@class = 'a-row a-spacing-none']/div[@class='a-row a-spacing-none']/a/span/text()").extract()
                book_comments_num_amzon = book.xpath("div[@class='s-item-container']/div[@class='a-row a-spacing-none']/div[@class='a-row a-spacing-top-mini a-spacing-none']/a/text()").extract()
                item["book_url_amzon"] = re.findall(".+(?=\/ref)",book_url_amzon[0].encode('utf-8'))[0]
                item["book_id_amzon"]  = re.findall("(?<=\/dp\/).+",item["book_url_amzon"])[0]
                item["book_name"] = book_name[0].encode('utf-8') if book_name != [] else ''
                item["book_comments_num_amzon"] = int(book_comments_num_amzon[0].encode('utf-8').replace(',','')) if book_comments_num_amzon != [] else 0
                item["book_price_amzon"] = ''.join(book_price_amzon).encode('utf-8')
                #价格解析
                if not self.bloomfilter.is_contains(item["book_url_amzon"]+item["book_price_amzon"]):
                    yield item
                    self.bloomfilter.insert(item["book_url_amzon"]+item["book_price_amzon"])
                self.redis_server.lpush('JdSlaver:start_urls',self.jd_search %  item["book_name"] + "&|" +item["book_id_amzon"])
            except Exception,e:
                self.logger.error(str(e))
                self.logger.error(response.url)
                self.logger.error(str(result_id))
        next_page = response.xpath("//a[@id='pagnNextLink']/@href").extract()
        if next_page != []:
            yield scrapy.Request(self.amzon_website_domin + next_page[0], callback=self.parse_data)