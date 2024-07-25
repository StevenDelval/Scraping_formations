import re
import scrapy
from formation.items import FranceCompetencesItem
from urllib.parse import urlparse
from scrapy.selector import Selector
from formation.models import *
from sqlalchemy.orm import sessionmaker

class FrancecompetencesSpider(scrapy.Spider):
    """
    Spider for scraping certification data from the France Compétences website.
    """
    name = "francecompetences"
    allowed_domains = ["francecompetences.fr"]
    base_url = "https://www.francecompetences.fr/recherche/"
    custom_settings = {
        'ITEM_PIPELINES': {
            'formation.pipelines.FranceCompetencesPipeline': 200,
            'formation.pipelines.FranceCompetencesDatabase': 300
        }
    }
    
    def start_requests(self):
        """
        Initializes the database session, fetches certification codes from the database, 
        and generates initial requests to be sent to the target website.
        """
        # Database session setup
        Session_sql = sessionmaker(bind=engine, autoflush=False)
        session_sql = Session_sql()
        
        # Fetching the codes from the database
        code_certifs = session_sql.query(FranceCompetences.code_certif).all()
        
        for code in code_certifs:
            match = re.match(r"([a-zA-Z]+)([0-9]+)", code[0])
            if match:
                letters, numbers = match.groups()
                url = f"{self.base_url}{letters}/{numbers}/"
                yield scrapy.Request(url=url, callback=self.parse)
        
        # Closing the database session
        session_sql.close()



    def parse(self, response):
        """
        Parses the response from the website, extracts relevant information, and populates the item.
        
        :param response: The response object containing the HTML content of the webpage.
        """
        
        item = FranceCompetencesItem()

        # Extract code_certif from the URL
        path_segments = urlparse(response.url).path.split('/')
        code_certif = f"{path_segments[-3].lower()}{path_segments[-2]}"
        item["code_certif"] = code_certif

        certificateur_rows = response.xpath(
            '//div[@class="accordion-content--fcpt-certification--certifier"]'
            '//table/tbody[@class="table--fcpt-certification__body"]/tr'
        )
        item["certificateurs"] = []

        for row in certificateur_rows:
            cells = row.xpath('td')
            certificateur = []
            for cell in cells:
                cell_text = cell.xpath('text()').get().strip() if cell.xpath('text()').get().strip() !="" else cell.xpath('a/text()').get().strip()
                certificateur.append(cell_text)
            
            item["certificateurs"].append(certificateur)


        item["est_actif"] = response.xpath('//div[@class="banner--fcpt-certification__body__tags"]/p[2]/span[2]/text()').get()
        item["niveau_de_qualification"] = response.xpath('//div[@class="list--fcpt-certification--essential--desktop__line"]/p[contains(normalize-space(), "niveau de qualification")]/../div/p/span/text()').get()
        item["date_echeance_enregistrement"] = response.xpath('//div[@class="list--fcpt-certification--essential--desktop__line"]/p[contains(normalize-space(), "Date d’échéance")]/../div/p/span/text()').get()
        item["titre"] = response.xpath('//h1/text()').get()
        
        item["formacodes"] = []
        formacodes_rows = response.xpath(
            '//div[@class="list--fcpt-certification--essential--desktop__line"]'
            '//p[@class="list--fcpt-certification--essential--desktop__line__title" and text()="Formacode(s)"]'
            '/following-sibling::div//p'
        )
        for forma_row in formacodes_rows:
            forma_row_content = ''.join(forma_row.getall())
            forma_row_selector = Selector(text=forma_row_content)
            span_text = forma_row_selector.xpath('//span/text()').get().strip() if forma_row_selector.xpath('//span/text()').get() != None else ""
            p_text = forma_row_selector.xpath('//p/text()[2]').get().strip() if forma_row_selector.xpath('//p/text()[2]').get() != None else ""

            concatenated_text = f"{span_text} {p_text}"
            item["formacodes"].append(concatenated_text)
        
        
        yield item   