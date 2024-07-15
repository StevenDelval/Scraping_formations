from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from formation.spiders.simplon import SimplonSpider
from formation.spiders.francecompetences import FrancecompetencesSpider

process = CrawlerProcess(get_project_settings())
process.crawl(SimplonSpider)
process.start()  # the script will block here until the crawling is finished
process = CrawlerProcess(get_project_settings())
process.crawl(FrancecompetencesSpider)
process.start()