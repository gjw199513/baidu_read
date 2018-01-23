# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from ..items import BookItem


class Top200Spider(scrapy.Spider):
    name = 'top200'
    allowed_domains = ['yuedu.baidu.com']
    start_urls = ['https://yuedu.baidu.com/rank/hotsale?pn=0']

    # 解析书籍列表页面
    def parse(self, response):
        # 提取每一本数书籍页面链接
        le = LinkExtractor(restrict_css='a.al.title-link')
        for link in le.extract_links(response):
            yield scrapy.Request(link.url, callback=self.parse_book)

        # 提取下一个列表的链接
        url = response.css('div.pager a.next::attr(href)').extract_first()
        if url:
            url = response.urljoin(url)
            yield scrapy.Request(url, callback=self.parse)

    # 解析一本书的页面
    def parse_book(self, response):
        sel = response.css('div.content-block')

        item = BookItem()
        item['name'] = sel.css('h1.book-title::attr(title)').extract_first()
        item['rating'] = sel.css('div.doc-info-score span.doc-info-score-value::text').extract_first()
        item['authors'] = sel.css('ul li.doc-info-author a::text').extract_first()

        # item['publisher'] = sel.css('ul li a.doc-info-field-val::text').extract()[1]
        item['publisher'] = sel.css('ul li').xpath('.//span[contains(string(.),"版权方")]/../a/text()').extract_first()

        # item['tags'] = sel.css('ul li.doc-info-tags div.content a::text').extract()
        item['tags'] = sel.css('ul li.doc-info-tags div.content').xpath('string(.)').re('\n+(\w+)')

        item['price'] = sel.css('span.confirm-price span.numeric::text').extract_first()

        yield item

