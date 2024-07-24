import requests
import re
import csv
import pandas
import psycopg2
import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
load_dotenv()

def fetch_data_from_azure():

    host=os.getenv("DB_HOSTNAME")
    port=int(os.getenv("DB_PORT"))
    password=os.getenv("DB_PASSWORD")
    user=os.getenv("DB_USERNAME")
    database=os.getenv("DB_NAME")


        # Create the connection URL
    connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    #connection_url = "sqlite:///database.db"


        # Create the SQLAlchemy engine
    engine = create_engine(connection_url, client_encoding='utf-8')
    print(connection_url)

        # Create a configured "Session" class
    Session = sessionmaker(bind=engine)

        # Create a session
    session = Session()

    # try:
                # Execute a query
    result = session.execute(text("""SELECT code_certif FROM france_competences"""))

            # Fetch all results from the executed query
    result_list = [row[0] for row in result]
    print(result_list)
    return result_list


    
def appel_api(code_certif):
    
    # Construire l'URL complète et appeler l'api
    base_url = "https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/moncompteformation_catalogueformation/records?where="
    prefixe = re.sub(r'\d+', '', code_certif)
    print(prefixe)

    if prefixe == 'rs' :
        endpoint="code_inventaire%3D"+re.sub(r"\D", "", code_certif) #code RS
        print(endpoint)

    elif prefixe == 'rncp' :
        endpoint="code_rncp%3D"+re.sub(r"\D", "", code_certif) #code_rncp
        print(endpoint)

    url = f"{base_url}{endpoint}"

        # Effectuer la requête GET
    response = requests.get(url) #, headers=headers, params=params
    data=response.json()

    print(data)
    return data



def nettoyage(data):
    pass




appel_api("rncp36061")



# result_list = fetch_data_from_azure()



















# data = pandas.read_csv("data.csv", sep=';', lineterminator ='\n')

#     # Extraire les colonnes spécifiques
# extracted_data = data[['date_extract', 'nom_departement']]
# print(extracted_data)




# # Enregistrer les données extraites dans un nouveau fichier CSV
# extracted_data.to_csv('extracted_data.csv', index=False)


#     data = pandas
# # Vérifier le statut de la réponse
# if response.status_code == 200:

    # response.content.to_csv('extracted_data.csv', index=False)


# # Afficher les données extraites
# print(extracted_data.head())













# # URL de base de l'API
# base_url = "https://opendata.caissedesdepots.fr/api.explore.com/v2.1/"

# # Endpoint spécifique de l'API
# endpoint = "catalog/datasets/moncompteformation_catalogueformation/exports/csv?where=nom_region%3D'Hauts-de-France'"
# # %20and%20(code_formacode_1%3D'15052'%20or%20code_formacode_2%3D'70322')&limit=20"

# # Votre clé API
# api_key = "456"

# # Paramètres de la requête (si nécessaire)
# params = {
#     # Ajoutez d'autres paramètres selon les besoins
# }

# # Headers de la requête (si nécessaire)
# headers = {
#     "Authorization": f"Bearer {api_key}",
#     "Content-Type": "application/json",
# }





    # # Connect to an existing database
    # # with psycopg.connect(f"postgresql://{user}:{password}@{host}:{port}") as conn:
    # with psycopg.connect(f"sqlite:///database.db") as conn:

    #     # Open a cursor to perform database operations
    #     with conn.cursor() as cur:

    #         # Execute a command: this creates a new table
    #         cur.execute("""
    #            SELECT code_certif FROM france_competences
    #             """)
    #         cur.fetchall
