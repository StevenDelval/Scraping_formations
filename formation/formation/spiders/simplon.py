import scrapy
from formation.items import FormationItem,SessionsItem
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.selector import Selector

class SimplonSpider(CrawlSpider):
    """
    Spider to crawl Simplon website and extract formation details.
    """
    name = "simplon"
    allowed_domains = ["simplon.co"]
    start_urls = ["https://simplon.co/notre-offre-de-formation.html"]
    # Custom settings for the spider
    custom_settings = {
        'ITEM_PIPELINES': {
            'formation.pipelines.SimplonPipeline': 200,
            'formation.pipelines.SimplonDatabase': 300
        }
    }
    # Define rules to follow links and parse items
    rules = [Rule(LinkExtractor(restrict_xpaths='//a[contains(text(),"Découvrez la formation")]'), callback='parse_item', follow=False),]

    def start_requests(self):
        """
        Start requests with Playwright enabled for handling JavaScript.
        """
        for url in self.start_urls:
            yield scrapy.Request(url, meta={"playwright": True}) #playwright permet d'avoir du javascript fonctionnel quand le scraper visite la page

    def parse_item(self, response):
        """
        Parse the formation page to extract information.
        """

        item = FormationItem()
        item['titre']= response.xpath('//h1/text()').get()
        item['rncp']= response.xpath('//a[contains(@href,"/rncp/")]/@href').get() #@href, là ou il y a la balise a
        item['rs']= response.xpath('//a[contains(@href,"/rs/")]/@href').getall() if len(response.xpath('//a[contains(@href,"/rs/")]/@href').getall()) else None
        
        # Check if the formation has RNCP or RS
        if item['rncp'] is not None or item['rs'] is not None :
            item['a_des_rs_rncp'] = True
        else:
            item['a_des_rs_rncp'] = False
        

        # Get the additional info link for sessions
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
        """
        Parse the additional information page to extract session details.
        """

        item = response.meta['item']
        item["sessions"] = []

        # Extract session details from the page
        sessions_divs = response.xpath('//div[@class="smp-bloc-card-session grid d-flex flex-wrap"]/div/div')
        for session_row in sessions_divs:
            session = SessionsItem()
            session_row_content = ''.join(session_row.getall())
            session_row_selector = Selector(text=session_row_content)
            
            # Extracting date of candidature
            day = session_row_selector.xpath('//span[@class="day"]/text()').get()
            month = session_row_selector.xpath('//span[@class="month"]/text()').get()
            year = session_row_selector.xpath('//div[@class="year"]/text()').get()
            day = day.strip() if day else ""
            month = month.strip() if month else ""
            year = year.strip() if year else ""
            if day and month and year:
                session['date_candidature'] = f"{day}/{month}/{year}"
            else:
                session['date_candidature'] = None
            # Extracting other session details    
            session['nom_session']= session_row_selector.xpath('//h2/text()').get()
            session['alternance']= session_row_selector.xpath('//div[@class="card-content-tag-container"]/div/a[contains(@href,"alternance")]/text()').get()
            session['distanciel']= session_row_selector.xpath('//div[@class="card-content-tag-container"]/div/a[contains(@href,"100-distanciel")]/text()').get()
            session['region'] = session_row_selector.xpath('//div[@class="card-session-info"]/i[contains(text(),"location_on")]/../text()').get()
            session['date_debut'] = session_row_selector.xpath('//div[@class="card-session-info calendar"]/i[contains(text(),"event")]/../text()').get()
            session['lieu'] = session_row_selector.xpath('//div[@class="card-content"]/text()').get()
            item["sessions"].append(session)
            
            
            

        # item['nom_session']= response.xpath('//h2/text()').get() #les sessiosn ouvertes
        # day = response.xpath('//span[@class="day"]/text()').getall()
        # month = response.xpath('//span[@class="month"]/text()').getall()
        # year = response.xpath('//div[@class="year"]/text()').getall()
        
        # if day and month and year:
        #     item['date_candidature'] = f"{day}/{month}/{year}"
        # else:
        #     item['date_candidature'] = None
        # item['alternance'] = response.xpath('//div[@class="card-content-tag-container"]/../text()').getall()
        # item['duree'] = response.xpath('normalize-space((//div[@class="card-session-info"]/i/following-sibling::text())[1])').getall()
        # item['region'] = response.xpath('//div[@class="card-session-info calendar"]').getall()
        # item['lieu'] = response.xpath('normalize-space((//div[@class="card-session-info"]/i/following-sibling::text())[3])').getall()
        # item['date_debut'] = response.xpath('normalize-space((//div[@class="card-session-info"]/i/following-sibling::text())[3])').getall()

        yield item






















