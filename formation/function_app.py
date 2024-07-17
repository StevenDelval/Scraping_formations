import logging
import os
import subprocess
import azure.functions as func
from azure.functions.decorators.core import AuthLevel
from dotenv import load_dotenv
load_dotenv()

app = func.FunctionApp()

@app.route(route="MyHttpTrigger", auth_level=func.AuthLevel.ANONYMOUS)
def MyHttpTrigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python timer trigger function executed.')

    try:
        # Change de répertoire vers le dossier contenant le projet Scrapy
        os.chdir("/home/site/wwwroot/formation")
        # Utiliser python -m scrapy pour exécuter le spider
        result = subprocess.run(["scrapy", "crawl", "simplon"], capture_output=True, text=True, check=True)
        result = subprocess.run(["scrapy", "crawl", "francecompetences"], capture_output=True, text=True, check=True)
        
        logging.info(result.stdout)
        logging.error(result.stderr)
        return func.HttpResponse("scrapping finish", status_code=200, mimetype="application/json")
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")