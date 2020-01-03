# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import MySQLdb

import codecs
import json

class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    # 自定义json文件的导出
    def __init__(self):
        self.file = codecs.open("article.json", "a", encoding="utf-8")

    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()

class JsonExporterPipeline(object):
    def __init__(self):
        self.file = open("article_export.json", "wb")
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def spider_closed(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


class ArticlespiderImagePipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            front_image_path = ""
            for ok, value in results:
                front_image_path = value["path"]
            item["front_image_path"] = front_image_path
        return item

class MysqlPipeline(object):
    def __init__(self):
        self.connection = MySQLdb.connect("127.0.0.1", "root", "mysql123", "article_spider", charset="utf8", use_unicode=True)
        self.cursor = self.connection.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            insert into cnblog_article(title, url, url_object_id, front_image_url, front_image_path, CommentCount, TotalView, DiggCount, BuryCount, create_time, tags, content)
            values(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE TotalView=values(TotalView), DiggCount=values(DiggCount), CommentCount=values(CommentCount)
        """
        params = list()
        params.append(item.get("title", ""))
        params.append(item.get("url", ""))
        params.append(item.get("url_object_id",""))
        front_image_url = item.get("front_image_url", [])
        front_image_url = ",".join(front_image_url)
        params.append(front_image_url)
        params.append(item.get("front_image_path", ""))
        params.append(item.get("CommentCount", 0))
        params.append(item.get("TotalView", 0))
        params.append(item.get("DiggCount", 0))
        params.append(item.get("BuryCount", 0))
        params.append(item.get("create_time", "1970-07-01"))
        params.append(item.get("tags", ""))
        params.append(item.get("content", ""))
        self.cursor.execute(insert_sql, tuple(params))
        self.connection.commit()
        return item
