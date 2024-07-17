import logging
import os
import subprocess
import azure.functions as func
from dotenv import load_dotenv
load_dotenv()
schedule = os.getenv("SCHEDULE")
app = func.FunctionApp()


@app.timer_trigger(schedule=schedule, arg_name="myTimer", run_on_startup=False, use_monitor=False)
def timer_trigger1(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function executed.')

    try:
        # Change de répertoire vers le dossier contenant le projet Scrapy
        os.chdir("/home/site/wwwroot/formation")
        # Utiliser python -m scrapy pour exécuter le spider
        result = subprocess.run(["scrapy", "crawl", "simplon"], capture_output=True, text=True, check=True)
        result = subprocess.run(["scrapy", "crawl", "francecompetences"], capture_output=True, text=True, check=True)
        
        logging.info(result.stdout)
        logging.error(result.stderr)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {e.stderr}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")