import logging
import os
import subprocess
from dotenv import load_dotenv
load_dotenv()


logging.info('Python timer trigger function executed.')
try:
    # Change de répertoire vers le dossier contenant le projet Scrapy
    os.chdir("/home/site/wwwroot/formation")
    
    # Utiliser python -m scrapy pour exécuter le spider
    logging.info('Simplon Spider executed.')
    simplon_result = subprocess.run(["scrapy", "crawl", "simplon"], capture_output=True, text=True, check=True)
    logging.info(f"Simplon Spider Output: {simplon_result.stdout}")
    
    logging.info('Francecompetences Spider executed.')
    francecompetences_result = subprocess.run(["scrapy", "crawl", "francecompetences"], capture_output=True, text=True, check=True)
    logging.info(f"Francecompetences Spider Output: {francecompetences_result.stdout}")

except subprocess.CalledProcessError as e:
    logging.error(f"Error executing command: {e.stdout}")
    logging.error(f"Error executing command: {e.stderr}")
except Exception as e:
    logging.error(f"Unexpected error: {str(e)}")
