import logging
import os
import subprocess
import azure.functions as func
from azure.functions.decorators.core import AuthLevel
from dotenv import load_dotenv
load_dotenv()

app = func.FunctionApp()

@app.timer_trigger(schedule="0 0 */2 * * *", arg_name="myTimer", run_on_startup=False, use_monitor=True)
def timer_trigger1(myTimer: func.TimerRequest) -> None:
    """
    Timer trigger function that runs every two days at midnight.

    Args:
        myTimer (func.TimerRequest): Timer request object provided by Azure Functions.

    This function changes the current directory to the folder containing the Scrapy project and
    runs two spiders: `simplon` and `francecompetences`. The output of each spider is logged.
    If there are any errors during the execution of the spiders, they are captured and logged.
    """
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