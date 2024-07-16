import os
from twisted.internet import asyncioreactor
import asyncio
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
asyncioreactor.install()
# Définir le réacteur à utiliser
os.environ['TWISTED_REACTOR'] = 'twisted.internet.asyncioreactor.AsyncioSelectorReactor'

from formation.spiders.simplon import SimplonSpider
from formation.spiders.francecompetences import FrancecompetencesSpider
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from scrapy.utils.log import configure_logging
from twisted.internet import reactor, defer

import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()


@app.route(route="ScrapyFunction", auth_level=func.AuthLevel.Anonymous)
def ScrapyFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    settings = get_project_settings()
    configure_logging(settings)
    runner = CrawlerRunner(settings)

    def crawl():
        print("SimplonSpider started crawling.")
        yield runner.crawl(SimplonSpider)
        print("SimplonSpider finished crawling.")
        print("FrancecompetencesSpider started crawling.")
        yield runner.crawl(FrancecompetencesSpider)
        print("FrancecompetencesSpider finished crawling.")
        reactor.stop()


    crawl()
    reactor.run() 


    return func.HttpResponse(
        "Scrapy spiders have been run.",
        status_code=200
    )