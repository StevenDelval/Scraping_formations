import scrapy
from ..items import FormationItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class SimplonSpider(CrawlSpider):
    name = "simplon"
    allowed_domains = ["simplon.co"]
    start_urls = ["https://simplon.co/notre-offre-de-formation.html"]

    rules = [Rule(LinkExtractor(restrict_xpaths='//a[contains(text(),"Découvrez la formation")]'), callback='parse_item', follow=False),]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True}) #playwright permet d'avoir du javascript fonctionnel quand le scraper visite la page

    def parse_item(self, response):

        item = FormationItem()
        item['title']= response.xpath('//h1/text()').get()
        item['rncp']= response.xpath('//a[contains(@href,"/rncp/")]/@href').get()
        item['rs']= response.xpath('//a[contains(@href,"/rs/")]/@href').get()
        yield item























