import scrapy


class SimplonSpider(scrapy.Spider):
    name = "simplon"
    allowed_domains = ["simplon.co"]
    start_urls = ["https://simplon.co"]

    def parse(self, response):
        pass
