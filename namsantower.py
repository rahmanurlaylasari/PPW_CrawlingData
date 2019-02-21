# -*- coding: utf-8 -*-
import scrapy


class NamsantowerSpider(scrapy.Spider):
    name = 'namsantower'
    allowed_domains = ['https://www.visitkorea.or.id/article/namsan-seoul-tower']
    start_urls = ['http://https://www.visitkorea.or.id/article/namsan-seoul-tower/']

    def parse(self, response):
        nama = response.css ('.entry-page ::text').extract()

        for item in zip (nama):
            scraped_info={
                'nama' : item [0]
                }
            yield scraped_info
