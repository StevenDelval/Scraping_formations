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


host=os.getenv("DB_HOSTNAME")
port=int(os.getenv("DB_PORT"))
password=os.getenv("DB_PASSWORD")
user=os.getenv("DB_USERNAME")
database=os.getenv("DB_NAME")


    # Create the connection URL
connection_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"

    # Create the SQLAlchemy engine
engine = create_engine(connection_url, echo=True)
print(connection_url)

    # Create a configured "Session" class
Session = sessionmaker(bind=engine)

    # Create a session
session = Session()

        # Execute a query
result = session.execute(text("""SELECT code_certif FROM france_competences"""))
print("lala")
        # Fetch all results from the executed query
result_list = [row[0] for row in result]


# Construire l'URL complète
for code_certif in result_list :
    prefixe = re.sub('1-9', '', code_certif)
    if prefixe == 'rs' :
        base_url = "https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/moncompteformation_catalogueformation/records?where=code_inventaire%3D"

        endpoint=re.sub(r"\D", "", code_certif) #code RS

    elif prefixe == 'rncp' :
        base_url = "https://opendata.caissedesdepots.fr/api/explore/v2.1/catalog/datasets/moncompteformation_catalogueformation/records?where=code_rncp%3D"
        endpoint=re.sub(r"\D", "", code_certif) #code_rncp

    url = f"{base_url}{endpoint}"


    # Effectuer la requête GET
    response = requests.get(url) #, headers=headers, params=params
    print(response)
    print(response.content)

#     data = pandas
# # Vérifier le statut de la réponse
# if response.status_code == 200:
#     # Définir le nom du fichier CSV
#     csv_file = "data.csv"

#     # Enregistrer le contenu de la réponse dans un fichier CSV
#     with open(csv_file, 'wb') as file:
#         file.write(response.content)
    
#     print(f"Les données CSV ont été enregistrées dans {csv_file}")
# else:
#     print(f"Erreur: {response.status_code}")
#     print(response.text)

# data = pandas.read_csv("data.csv", sep=';', lineterminator ='\n')

# # Extraire les colonnes spécifiques
# extracted_data = data[['date_extract', 'nom_departement']]

# # Afficher les données extraites
# print(extracted_data.head())

# # Enregistrer les données extraites dans un nouveau fichier CSV
# extracted_data.to_csv('extracted_data.csv', index=False)












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