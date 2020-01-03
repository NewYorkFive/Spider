# -*- coding: utf-8 -*-
import re
import json
from urllib import parse

import scrapy
from scrapy import Request
import requests

from ArticleSpider.items import CnblogsArticleItem
from ArticleSpider.utils import common


class CnblogsSpider(scrapy.Spider):
    name = 'cnblogs'
    allowed_domains = ['news.cnblogs.com']
    start_urls = ['http://news.cnblogs.com/']

    def parse(self, response):
        # 1. 获取新闻列表页面中的新闻url并交给scrapy进行下载后调用相应的解析方法
        # 2. 获取下一页的url并交给scrapy进行下载，下载完成后交给parse继续跟进
        nodes = response.xpath('//*[@id="news_list"]//div[@class="content"]')[1:2]

        for node in nodes:
            # href = node.xpath('h2[@class="news_entry"]/a/@href').extract()
            post_url = node.xpath('h2/a/@href').extract_first("")
            image_a = node.xpath('div[@class="entry_summary"]/a')
            image_url = image_a.xpath('img/@src').extract_first("")
            if image_url != '':
                image_url = parse.urljoin(response.url, image_url)
            image_url = [image_url]
            else:
                image_url = []
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url":image_url}, callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.xpath('//div[@class="pager"]/a[contains(text(),"Next >")]/@href').extract_first("")
        # yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)
        
        print(next_url)

    def parse_detail(self, response):
        matches = re.match(".*/(?P<contentId>[0-9]+)", response.url)
        if matches:
            article_item = CnblogsArticleItem()
            title = response.xpath('//div[@id="news_title"]/a/text()').extract_first("")
            news_info_node = response.xpath('//div[@id="news_info"]')
            create_time = news_info_node.xpath('span[@class="time"]/text()').extract_first("")
            matches2 = re.match(".*?(?P<create_time>[0-9:-]+[\s]*?[0-9:-]+).*", create_time)
            # .*?(?P<create_time>\d.*)
            # .*?(?P<create_time>[0-9:-]+[\s]*?[0-9:-]+).*
            if matches2:
                create_time = matches2["create_time"]
            content = response.xpath('//*[@id="news_content"]').extract_first("")

            tag_list = response.xpath('//*[@id="news_more_info"]/div[@class="news_tags"]/a/text()').extract()
            tags = ",".join(tag_list)

            article_item["title"] = title
            article_item["create_time"] = create_time
            article_item["content"] = content
            article_item["tags"] = tags
            article_item["url"] = response.url
            article_item["url_object_id"] = common.get_md5(response.url)
            article_item["front_image_url"] = response.meta.get("front_image_url", "")

            contentId = matches["contentId"]
            url = parse.urljoin(response.url, "https://news.cnblogs.com/NewsAjax/GetAjaxNewsInfo?contentId={}".format(contentId))
            yield Request(url=url, meta={"article_item": article_item}, callback=self.parse_news_info)



    def parse_news_info(self,response):

        article_item = response.meta.get("article_item", "")

        json_data = json.loads(response.text)
        article_item["CommentCount"] = json_data["CommentCount"]
        article_item["TotalView"] = json_data["TotalView"]
        article_item["DiggCount"] = json_data["DiggCount"]
        article_item["BuryCount"] = json_data["BuryCount"]
        yield article_item
