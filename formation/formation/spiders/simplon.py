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
        item['rncp']= response.xpath('//a[contains(@href,"/rncp/")]/@href').get() #@href, là ou il y a la balise a
        item['rs']= response.xpath('//a[contains(@href,"/rs/")]/@href').get()
        

        
        # item['rncp']= response.xpath
        yield item

        additional_info_link = response.xpath('//a[contains(@href,"/i-apply/")]/@href').get()
        if additional_info_link:
            additional_info_url = response.urljoin(additional_info_link)
            request = scrapy.Request(additional_info_url, callback=self.parse_additional_info)
            request.meta['item'] = item
            request.meta.update({"playwright": True})

            yield request
        else:
            yield item

    def parse_additional_info(self, response):
        item = response.meta['item']
        item['nom_session']= response.xpath('//h2/text()').get() #les sessiosn ouvertes
        #item['additional_info'] = response.xpath('//div[@class="additional-info-class"]/text()').get()
        day = response.xpath('//span[@class="day"]/text()').getall()
        month = response.xpath('//span[@class="month"]/text()').getall()
        year = response.xpath('//div[@class="year"]/text()').getall()
        
        if day and month and year:
            item['date_candidature'] = f"{day}/{month}/{year}"
        else:
            item['date_candidature'] = None
        item['alternance'] = response.xpath('//div[@class="card-content-tag-container"]/../text()').getall()
        item['durée'] = response.xpath('normalize-space((//div[@class="card-session-info"]/i/following-sibling::text())[1])').getall()
        item['region'] = response.xpath('//div[@class="card-session-info calendar"]').getall()
        item['lieu'] = response.xpath('normalize-space((//div[@class="card-session-info"]/i/following-sibling::text())[3])').getall()
        item['date_debut'] = response.xpath('normalize-space((//div[@class="card-session-info"]/i/following-sibling::text())[3])').getall()

        yield item






















