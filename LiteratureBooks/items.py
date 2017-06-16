# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
# from scrapy.loader import ItemLoader
# from scrapy.loader.processors import MapCompose, TakeFirst, Join


class LiteraturebooksItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    book_name = scrapy.Field()
    book_comments_num_amzon = scrapy.Field()
    book_price_amzon = scrapy.Field()
    book_url_amzon = scrapy.Field()
    book_id_amzon = scrapy.Field()
class JdBooksItem(scrapy.Item):
    book_name = scrapy.Field()
    book_id_amzon = scrapy.Field()
    book_url_jd = scrapy.Field()
    book_comments_num_jd = scrapy.Field()
    book_price_jd = scrapy.Field()
# class LiteraturebooksLoader(ItemLoader):
    # default_item_class = LiteraturebooksItem
    # default_input_processor = MapCompose(lambda s: s.strip())
    # default_output_processor = TakeFirst()
    # description_out = Join()
