import scrapy
from ..items import FranceCompetencesItem

class FrancecompetencesSpider(scrapy.Spider):
    name = "francecompetences"
    allowed_domains = ["francecompetences.fr"]
    start_urls = ["https://www.francecompetences.fr/recherche/rncp/37682/","https://www.francecompetences.fr/recherche/rs/5487/","https://www.francecompetences.fr/recherche/rncp/37827/"]

    def parse(self, response):
        item = FranceCompetencesItem()
        certificateur_rows = response.xpath(
            '//div[@class="accordion-content--fcpt-certification--certifier"]'
            '//table/tbody[@class="table--fcpt-certification__body"]/tr'
        )
        item["certificateur"] = []

        for row in certificateur_rows:
            cells = row.xpath('td')
            certificateur = []
            for cell in cells:
                cell_text = cell.xpath('text()').get().strip() if cell.xpath('text()').get().strip() !="" else cell.xpath('a/text()').get().strip()
                certificateur.append(cell_text)
            
            item["certificateur"].append(certificateur)
        
        
        yield item   