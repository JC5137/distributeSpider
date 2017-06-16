# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy import log
from twisted.enterprise import adbapi
from datetime import datetime
import MySQLdb
import MySQLdb.cursors

class LiteraturebooksPipeline(object):
    def __init__(self,dbpool):
        self.dbpool = dbpool
    @classmethod
    def from_settings(cls, settings):
        mysql_args = dict(
            host=settings['MYSQL_HOST'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode= True,
        )
        dbpool = adbapi.ConnectionPool('MySQLdb', **mysql_args)
        return cls(dbpool)
    #pipeline默认调用
    def process_item(self, item, spider):
        if "Amzon" in spider.name:
            d = self.dbpool.runInteraction(self._do_insert, item, spider)
            d.addErrback(self._handle_error, item, spider)
            d.addBoth(lambda _: item)
            return d
        if "Jd" in spider.name:
            d = self.dbpool.runInteraction(self._do_update, item, spider)
            d.addErrback(self._handle_error, item, spider)
            d.addBoth(lambda _: item)
            return d 
    #将每行更新或写入数据库中
    def _do_insert(self, conn, item, spider):
        parms = (item["book_id_amzon"],item["book_url_amzon"],item['book_name'],item['book_comments_num_amzon'],item['book_price_amzon'])
        sql = """insert into book_info 
                (book_id_amzon,
                 book_url_amzon,
                 book_name,
                 book_comments_num_amzon,
                 book_price_amzon
                )
                values ('%s','%s','%s',%d,'%s')""" %parms
        conn.execute(sql)
    def _do_update(self, conn, item, spider):
        parms = (item["book_url_jd"],item["book_comments_num_jd"],item["book_price_jd"],item["book_name"],item["book_id_amzon"])
        sql = """update book_info set
                 book_url_jd = '%s',
                 book_comments_sum_jd = '%d',
                 book_price_jd = '%s' 
                 where book_name = '%s' and book_id_amzon = '%s'""" %parms
        print sql
        conn.execute(sql)
    #异常处理
    def _handle_error(self, failue, item, spider):
        log.error(failure)
