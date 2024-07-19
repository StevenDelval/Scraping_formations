import logging
import os
import subprocess
import azure.functions as func
from azure.functions.decorators.core import AuthLevel
from dotenv import load_dotenv
load_dotenv()

app = func.FunctionApp()

@app.timer_trigger(schedule="0 */30 * * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def timer_trigger1(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

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