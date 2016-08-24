# -*- coding: utf-8 -*-
import scrapy,json,urllib
from scrapy.http import Request
from pj12306.items import AgenciesItem,CommitItem


class AgenciesSpider(scrapy.Spider):
    name = "agencies"
    # start_urls = (
    #     'https://kyfw.12306.cn/otn/userCommon/allProvince',
    # )
    custom_settings = {
        'ITEM_PIPELINES' : {
        'pj12306.pipelines.AgenciesPipeline': 300,
    },
        'DUPEFILTER_DEBUG': True,
        'DUPEFILTER_CLASS': "pj12306.filter.URLTurnFilter",
        'JOBDIR': "s/agencys",
        'DOWNLOADER_MIDDLEWARES': {
            'pj12306.middle.DownloaderMiddleware': 500,
        },
    }

    def __init__(self, *a, **kw):
        super(AgenciesSpider, self).__init__(self.name, **kw)
        self.turn = a[0]
        self.logger.info("%s. this turn %d" % (self.name, self.turn))
    def start_requests(self):
        url = 'https://kyfw.12306.cn/otn/userCommon/allProvince'
        yield Request(url=url,callback=self.parse,meta={'turn':self.turn})
    def parse(self, response):
        url = 'https://kyfw.12306.cn/otn/queryAgencySellTicket/query?'
        datas = json.loads(response.body)
        for data in datas['data']:
            params = {'province':data['chineseName'].encode('utf-8'),'city':'','county':''}
            ful_url = url + urllib.urlencode(params)
            yield Request(ful_url,callback=self.parse_agency,meta={'turn':response.meta['turn']})

    def parse_agency(self,response):
        js_file = json.loads(response.body)
        for data in js_file['data']['datas']:
            item = AgenciesItem()
            item['province'] = data['province']
            item['city'] = data['city']
            item['county'] = data['county']
            item['address'] = data['address']
            item['name'] = data['agency_name']
            item['windows'] = data['windows_quantity']
            item['start'] = data['start_time_am']
            item['end'] = data['stop_time_pm']
            item['turn'] = response.meta['turn']
            yield item
        yield CommitItem()

