import requests
import re
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

def fetch_data_from_azure():

    """
    Fetch data from an Azure-hosted PostgreSQL database.
    
    This function retrieves connection details from environment variables,
    establishes a connection to the database, executes a query to fetch 
    certification codes, and returns the result as a list.

    Returns:
        list: A list of certification codes fetched from the database.
    """

    host=os.getenv("DB_HOSTNAME")
    port=int(os.getenv("DB_PORT"))
    password=os.getenv("DB_PASSWORD")
    user=os.getenv("DB_USERNAME")
    database=os.getenv("DB_NAME")

        # Create the connection URL
    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"     #connection_url = "sqlite:///database.db"
    
        # Create the SQLAlchemy engine
    engine = create_engine(connection_url, client_encoding='utf-8')

        # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

        # Create a session
    session = Session()

        # Execute a query
    result = session.execute(text("""SELECT code_certif FROM france_competences"""))

        # Fetch all results from the executed query
    result_list = [row[0] for row in result]
    print(result_list)
    return result_list


    
def appel_api(code_certif):

    """
    Call the external API to retrieve data based on the certification code (RS or RNCP).
    
    This function constructs the appropriate API endpoint based on the 
    prefix of the certification code and sends a GET request to fetch the data.

    Args:
        code_certif (str): The certification code used to query the API.

    Returns:
        dict: The JSON response from the API.
    """
    
    # Construire l'URL complète et appeler l'api
    base_url = "https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/moncompteformation_catalogueformation/records?where="
    prefixe = re.sub(r'\d+', '', code_certif)

    if prefixe == 'rs' :
        endpoint="code_inventaire="+re.sub(r"\D", "", code_certif) #code RS

    elif prefixe == 'rncp' :
        endpoint="code_rncp="+re.sub(r"\D", "", code_certif) #code_rncp

    url = f"{base_url}{endpoint}"

        # Effectuer la requête GET
    response = requests.get(url) #, headers=headers, params=params
    data=response.json()

    return data



def nettoyage(data):

    """
    Clean and select specific fields from the API response data.
    
    This function extracts specified fields from the results within the 
    API response and returns a list of dictionaries containing these fields.

    Args:
        data (dict): The JSON data returned by the API.

    Returns:
        list: A list of dictionaries containing the selected fields.
    """
  
    # Select specific fields
    fields_to_keep = ["intitule_certification", "intitule_formation", "nom_departement",
                      "nom_region", "code_formacode_1", "code_formacode_2",
                      "code_formacode_3","code_formacode_4","code_formacode_5"]

    # Extract the selected fields from the results
    selected_data = []
    for result in data['results']:
        selected_result = {field: result[field] for field in fields_to_keep}
        selected_data.append(selected_result)

    return selected_data
