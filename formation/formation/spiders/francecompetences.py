import scrapy
from ..items import FranceCompetencesItem
from scrapy.selector import Selector

class FrancecompetencesSpider(scrapy.Spider):
    name = "francecompetences"
    allowed_domains = ["francecompetences.fr"]
    start_urls = ["https://www.francecompetences.fr/recherche/rncp/37682/","https://www.francecompetences.fr/recherche/rncp/34757/","https://www.francecompetences.fr/recherche/rs/5487/","https://www.francecompetences.fr/recherche/rncp/37827/"]

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
        item["est_actif"] = response.xpath('//div[@class="banner--fcpt-certification__body__tags"]/p[2]/span[2]/text()').get()
        item["niveau_de_qualification"] = response.xpath('//div[@class="list--fcpt-certification--essential--desktop__line"]/p[contains(normalize-space(), "niveau de qualification")]/../div/p/span/text()').get()
        item["date_echeance_enregistrement"] = response.xpath('//div[@class="list--fcpt-certification--essential--desktop__line"]/p[contains(normalize-space(), "Date d’échéance")]/../div/p/span/text()').get()
        item["title"] = response.xpath('//h1/text()').get()
        
        item["formacodes"] = []
        formacodes_rows = response.xpath(
            '//div[@class="list--fcpt-certification--essential--desktop__line"]'
            '//p[@class="list--fcpt-certification--essential--desktop__line__title" and text()="Formacode(s)"]'
            '/following-sibling::div//p'
        )

        for forma_row in formacodes_rows:
            forma_row_content = ''.join(forma_row.getall())
            forma_row_selector = Selector(text=forma_row_content)
            span_text = forma_row_selector.xpath('//span/text()').get()
            p_text = forma_row_selector.xpath('//p/text()[2]').get()

            concatenated_text = f"{span_text.strip()} {p_text.strip()}"
            item["formacodes"].append(concatenated_text)
        
        
        yield item   