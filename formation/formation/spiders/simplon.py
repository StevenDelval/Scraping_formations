import scrapy
from ..items import FormationItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

class SimplonSpider(CrawlSpider):
    name = "simplon"
    allowed_domains = ["simplon.co"]
    start_urls = ["https://simplon.co/notre-offre-de-formation.html"]
    custom_settings = {
        'ITEM_PIPELINES': {
            'formation.pipelines.SimplonPipeline': 200,
            'formation.pipelines.SimplonDatabase': 300
        }
    }
    rules = [Rule(LinkExtractor(restrict_xpaths='//a[contains(text(),"Découvrez la formation")]'), callback='parse_item', follow=False),]

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True}) #playwright permet d'avoir du javascript fonctionnel quand le scraper visite la page

    def parse_item(self, response):

        item = FormationItem()
        item['title']= response.xpath('//h1/text()').get()
        item['rncp']= response.xpath('//a[contains(@href,"/rncp/")]/@href').get() #@href, là ou il y a la balise a
        item['rs']= response.xpath('//a[contains(@href,"/rs/")]/@href').get()

        if item['rncp'] is not None or item['rs'] is not None :
            item['a_des_rs_rncp'] = True
        else:
            item['a_des_rs_rncp'] = False
        


        additional_info_link = response.xpath('//a[contains(@href,"/i-apply/")]/@href').get()
        if additional_info_link:
            additional_info_url = response.urljoin(additional_info_link)
            request = scrapy.Request(additional_info_url, callback=self.parse_additional_info)
            request.meta['item'] = item
            request.meta.update({"playwright": True})
            item['a_des_sessions'] = True
            yield request
        else:
            item['a_des_sessions'] =  False
            yield item

    def parse_additional_info(self, response):
        item = response.meta['item']
        item['nom_session']= response.xpath('//h2/text()').get() #les sessiosn ouvertes
        item['additional_info'] = response.xpath('//div[@class="additional-info-class"]/text()').get()
        day = response.xpath('//span[@class="day"]/text()').get()
        month = response.xpath('//span[@class="month"]/text()').get()
        year = response.xpath('//div[@class="year"]/text()').get()
        

        if day and month and year:
            item['date'] = f"{day}/{month}/{year}"
        else:
            item['date'] = None
        # item['alternance'] = response.xpath('//div[@class="card-content-tag-container"]/../text()').getall()
        yield item






















