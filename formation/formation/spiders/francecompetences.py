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
        certificateur_tr_texts = certificateur_selector.xpath('//tr').getall()
        for tr in certificateur_tr_texts:
            certificateur_tr_content = ''.join(tr)
            certificateur_tr_selector = Selector(text=certificateur_tr_content)
            certificateur_td_texts = certificateur_tr_selector.xpath('//td').getall()
            
            for i,elt in enumerate(certificateur_td_texts):
                td_selector = Selector(text=elt)
                td_texts = td_selector.xpath('//td/text()').get()
                td_texts = td_texts.replace('\n', '')\
                            .replace('\t', '')\
                            .strip(" ")
                if td_texts == "":
                    td_texts = td_selector.xpath('//td/a/text()').get()\
                            .replace('\n', '')\
                            .replace('\t', '')\
                            .strip(" ")
                    
                print(i,td_texts.replace('\n', '')\
                            .replace('\t', '')\
                            .strip(" "))

        base_legal = response.xpath('//div[@class="accordion-content--fcpt-certification--legal-basis"]/table').extract()
        base_legal_content = ''.join(base_legal)
        base_legal_selector = Selector(text=base_legal_content)
        base_legal_tr = base_legal_selector.xpath('//tr').getall()
        for tr in base_legal_tr:
            tr_selector = Selector(text=tr)
            th_text = tr_selector.xpath('//th/text()').get().replace('\n', '')\
                                                                    .replace('\t', '')\
                                                                    .strip()
            td_text = tr_selector.xpath('//td/text()').get()\
                                                        .replace('\n', '')\
                                                        .replace('\t', '')\
                                                        .strip()
            match th_text:
                case "Date de décision":
                   print(td_text)
                case "Durée de l'enregistrement en années":
                   print(td_text)
                case "Date d'échéance de l'enregistrement":
                   print(td_text)
                case "Date de dernière délivrance possible de la certification ":
                   print(td_text)

        

        