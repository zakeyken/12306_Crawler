# -*- coding: utf-8 -*-
from scrapy.http.request import Request
from pj12306.items import *

class StationsSpider(scrapy.Spider):
    name = 'StationsSpider'
    # start_urls = ['http://www.12306.cn/mormhweb/kyyyz/']

    custom_settings = {
            'ITEM_PIPELINES': {
                'pj12306.pipelines.StationSQLPipeline': 300,
            },
            'DUPEFILTER_DEBUG':True,
            'DUPEFILTER_CLASS':'pj12306.filter.URLTurnFilter',
            'JOBDIR': "s/stations",
            'DOWNLOADER_MIDDLEWARES': {
                'pj12306.middle.DownloaderMiddleware': 500,
            },
    }
    def __init__(self,*a,**kw):
        super(StationsSpider,self).__init__(self.name,**kw)
        self.turn = a[0]
        self.logger.info('%s. this turn %d' % (self.name,self.turn))

    def start_requests(self):
        url = 'http://www.12306.cn/mormhweb/kyyyz/'
        yield Request(url=url,callback=self.parse,meta={'turn':self.turn})

    def parse(self, response):
        names = response.xpath('//*[@id="secTable"]/tbody/tr/td/text()').extract()
        sub_urls = response.xpath('//*[@id="mainTable"]/descendant::a[@target="frameCon"]/@href').extract()

        for i,item in enumerate(sub_urls):
            url = response.url + item[2:]
            if i % 2 == 0:
                yield Request(url,callback=self.parse_station,meta={'bureau':names[i/2], 'turn':response.meta['turn'],'station':True})
                continue
            else:
                yield Request(url,callback=self.parse_station,meta={'bureau':names[i/2], 'turn':response.meta['turn'], 'station':False})



    def parse_station(self, response):
        datas = response.css("table table tr")
        if len(datas) <= 2:
            return
        for i in range(0, len(datas)):
            if i < 2:
                continue
            infos = datas[i].css("td::text").extract()

            item = StationItem()
            item["bureau"] = response.meta["bureau"]
            item["station"] = response.meta["station"]
            item["name"] = infos[0]
            item["address"] = infos[1]
            item["passenger"] = infos[2].strip() != u""
            item["luggage"] = infos[3].strip() != u""
            item["package"] = infos[4].strip() != u""
            item['turn'] = response.meta['turn']
            yield item

        yield CommitItem()
          



