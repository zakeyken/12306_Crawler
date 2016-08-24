# -*-coding:utf-8 -*-
import datetime,json,urllib,time
from scrapy.http.request import Request
from pj12306.items import *

class ScheduleSpider(scrapy.Spider):
    name = 'ScheduleSpider'


    custom_settings = {
            'ITEM_PIPELINES': {
                'pj12306.pipelines.SQLPipeline': 300,
            },
            'DUPEFILTER_DEBUG': True,
            'DOWNLOADER_MIDDLEWARES': {
                'pj12306.middle.DownloaderMiddleware': 500,
            },
            'DUPEFILTER_CLASS': "pj12306.filter.URLTurnFilter",
            'JOBDIR':'s/station_list',
    }

    def __init__(self, *a, **kw):
        super(ScheduleSpider, self).__init__(self.name, **kw)
        self.turn = a[0]
        self.logger.info("%s. this turn %d" % (self.name, self.turn))



    def start_requests(self):
        url = "https://kyfw.12306.cn/otn/queryTrainInfo/getTrainName?"
        t = (datetime.datetime.now() + datetime.timedelta(days = 3)).strftime("%Y-%m-%d")
        params = {"date":t}

        s_url = url + urllib.urlencode(params)
        self.logger.debug("start url " + s_url)
        yield Request(s_url, callback = self.parse, meta = {"t":t,'turn':self.turn})

    def parse(self, response):
        datas = json.loads(response.body)
        url = "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?"
        for data in datas["data"]:
            item = BriefItem()
            briefs = data["station_train_code"].split("(")
            item["train_no"] = data["train_no"]
            item["code"] = briefs[0]
            briefs = briefs[1].split("-")
            item["start"] = briefs[0]
            item["end"] = briefs[1][:-1]
            # item['seat_type'] = ''
            item['turn'] = response.meta['turn']
            yield item

            params = u"train_no=" + data["train_no"] + u"&from_station_telecode=BBB&to_station_telecode=BBB&depart_date=" + response.meta["t"]

            yield Request(url + params, callback = self.parse_train_schedule, meta = {"train_no":data["train_no"],'turn':response.meta['turn']})

    def parse_train_schedule(self, response):
        stations = json.loads(response.body)
        datas = stations["data"]["data"]
        size = len(datas)
        for i,data in enumerate(datas):
            info = InfoItem()
            info["train_no"] = response.meta["train_no"];
            info["no"] = int(data["station_no"])
            info["station"] = data["station_name"]
            info['turn'] = response.meta['turn']
#判断站点在列车时刻表中的位置，0为始发站，1为终到站，2为经停站。
            if i == 0:
                info["type"] = 0
            elif i == size-1:
                info["type"] = 1
            else:
                info["type"] = 2

            if data["start_time"] != u"----":
                info["start_time"] = data["start_time"] + u":00"
            else:
                info["start_time"] = None

            if data["arrive_time"] != u"----":
                info["arrive_time"] = data["arrive_time"] + u":00"
            else:
                info["arrive_time"] = None

            stop = data["stopover_time"]
            if stop != u"----":
                if stop.endswith(u"分钟"):
                    info["stopover_time"] = u"00:" + stop[:stop.find(u"分钟")] + u":00"
                else:
                    info["stopover_time"] = stop + u":00"
            else:
                info["stopover_time"] = None

            yield info
        yield CommitItem()


