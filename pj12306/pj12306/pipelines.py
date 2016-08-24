# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
from scrapy.exceptions import DropItem
from pj12306.items import *
from scrapy.log import logger

# class ProvincePipeline1(object):
#     def process_item(self, item, spider):
#         if isinstance(item,CommitItem):
#             pass
#         else:
#             if item["name"]:
#                     return item
#             else:
#                 raise DropItem("none item")
#
# class ProvincePipeline2(object):
#     def process_item(self, item, spider):
#         print item["name"], "--------"
#         return item

class AgenciesPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306,
                                    user='12306',
                                    password='12306',
                                    db='12306-train',
                                    charset='utf8')
        self.cursor = self.conn.cursor()
        self.sql = "INSERT IGNORE INTO agencys (`province`, `city`,\
                `county`, `address`, `name`, `windows`,\
                `start`, `end`,`turn`) VALUES\
                (%s, %s, %s, %s, %s, %s, %s, %s, %s)"

    def process_item(self, item, spider):
            try:
                if isinstance(item, CommitItem):
                    self.conn.commit()
                else:

                    self.cursor.execute(self.sql, (item["province"], item["city"],
                                               item["county"], item["address"],
                                               item["name"], item["windows"],
                                               item["start"] + u'00',
                                               item["end"] + u'00',item["turn"]))
            except Exception , e:
                logger.warning("execute sql fail.")
                logger.warning(str(e))
                logger.warning(item)

class StationSQLPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306,
                                    user='12306',
                                    password='12306',
                                    db='12306-train',
                                    charset='utf8')
        self.cursor = self.conn.cursor()
        self.sql = "INSERT IGNORE INTO `stations` (`bureau`, `station`,\
                `name`, `address`, `passenger`, `luggage`,\
                `package`,`turn`) VALUES\
                (%s, %s, %s, %s, %s, %s, %s, %s)"

    def process_item(self, item, spider):
        if isinstance(item, CommitItem):
            try:
                self.conn.commit()
            except Exception as e:
                logger.info('commit failed!')

        else:
            self.cursor.execute(self.sql, (item["bureau"], item["station"],
                                           item["name"], item["address"],
                                           item["passenger"], item["luggage"],
                                           item["package"],item["turn"]))

class SQLPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='localhost', port=3306,
                                    user='12306',
                                    password='12306',
                                    db='12306-train',
                                    charset='utf8')
        self.cursor = self.conn.cursor()
        self.brief_sql = "INSERT IGNORE INTO `train_briefs` VALUES\
                    (%s, %s, %s, %s, null, %s)"
        self.info_sql = "INSERT IGNORE INTO `train_infos` VALUES\
                    (%s, %s, %s, %s, %s, %s, %s)"
        self.turn_sql = "INSERT IGNORE INTO `turns` VALUES\
                    (%s, %s)"

    def process_item(self, item, spider):
        try:
            if isinstance(item, CommitItem):
                self.conn.commit()
            elif isinstance(item, BriefItem):
                self.cursor.execute(self.brief_sql, (item["code"],
                                                     item["train_no"],
                                                     item["start"], item["end"], item["turn"]))
            elif isinstance(item, InfoItem):
                self.cursor.execute(self.info_sql, (item["train_no"],
                                                    item["no"],
                                                    item["station"],
                                                    item["start_time"], item["arrive_time"],
                                                    item["stopover_time"], item["turn"]))
            else:
                self.cursor.execute(self.turn_sql, (item["id"],
                                                    item["mark_time"]))
                self.conn.commit()
        except Exception, e:
            logger.warning("excute sql fail.")
            logger.warning(str(e))

class TicketSQLPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host = 'localhost', port = 3306,
                                        user = '12306',
                                        password = '12306',
                                        db = '12306-train',
                                        charset = 'utf8')
        self.cursor = self.conn.cursor()
        self.update_brief = 'UPDATE train_briefs SET seat_type=%s WHERE code=%s and turn= %s'
        self.station_sql = "INSERT IGNORE INTO `train_stations` VALUES\
                    (%s, %s, %s)"
        self.tickets_sql = "INSERT IGNORE INTO `train_tickets` VALUES\
                    (%s, %s, %s, %s, %s, %s, %s, %s,\
                    %s, %s, %s, %s, %s, %s, %s)"

    def process_item(self, item, spider):
        try:
            if isinstance(item, CommitItem):
                self.conn.commit()
            elif isinstance(item, BriefDeltaItem):
                self.cursor.execute(self.update_brief, (item["seat_type"],
                    item["code"]))
            elif isinstance(item, CodeItem):
                self.cursor.execute(self.station_sql, (item["name"],
                    item["code"]))
            else:
                self.cursor.execute(self.tickets_sql, (item["train_no"],
                    item["start"], item["end"], item["swz"],
                    item["tz"], item["zy"], item["ze"],
                    item["gr"], item["rw"], item["yw"],
                    item["rz"], item["yz"], item["wz"],
                    item["qt"],item['turn']))
        except Exception, e:
            spider.logger.warning("execute sql fail.")
            spider.logger.warning(str(e))

