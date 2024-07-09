import scrapy
from scrapy.selector import Selector

class FrancecompetencesSpider(scrapy.Spider):
    name = "francecompetences"
    allowed_domains = ["francecompetences.fr"]
    start_urls = ["https://www.francecompetences.fr/recherche/rncp/37682/","https://www.francecompetences.fr/recherche/rs/5487/","https://www.francecompetences.fr/recherche/rncp/37827/"]

    def parse(self, response):
        certificateur =response.xpath('//div[@class="accordion-content--fcpt-certification--certifier"]/div/table/tbody[@class="table--fcpt-certification__body"]').extract()
        certificateur_content = ''.join(certificateur)
        certificateur_selector = Selector(text=certificateur_content)
        certificateur_td_texts = certificateur_selector.xpath('//td/text()').getall()
        print(certificateur_td_texts)
        for i,elt in enumerate(certificateur_td_texts):
            print(i,elt.replace('\n', '')\
                        .replace('\t', '')\
                        .strip(" "))

        base_legal = response.xpath('//div[@class="accordion-content--fcpt-certification--legal-basis"]/table/tbody').extract()
        base_legal_content = ''.join(base_legal)
        base_legal_selector = Selector(text=base_legal_content)
        base_legal_tr = base_legal_selector.xpath('//tr').getall()
        for tr in base_legal_tr:
            tr_selector = Selector(text=tr)
            th_text = tr_selector.xpath('//th/text()').get().replace('\n', '')\
                                                                    .replace('\t', '')\
                                                                    .strip()
            td_text = tr_selector.xpath('//td/text()').get()
            match th_text:
                case "Date de décision":
                   print(td_text)
                case "Durée de l'enregistrement en années":
                   print(td_text)
                case "Date d'échéance de l'enregistrement":
                   print(td_text)
                case "Date de dernière délivrance possible de la certification ":
                   print(td_text)

        

        