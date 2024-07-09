import requests
import os

# URL du fichier CSV
url = 'https://www.data.gouv.fr/fr/datasets/r/205a72c5-725a-40c0-9c39-073454bdd553'

# Nom du fichier à enregistrer
filename = 'moncompteformation_catalogueformation.csv'

# Obtenir le répertoire de travail actuel
current_directory = os.getcwd()

# Chemin complet pour sauvegarder le fichier
file_path = os.path.join(current_directory, filename)

# Téléchargement du fichier
response = requests.get(url)

# Vérifiez que la requête a réussi (statut code 200)
if response.status_code == 200:
    # Écrire le contenu dans un fichier local
    with open(file_path, 'wb') as file:
        file.write(response.content)
    print(f'Fichier {filename} téléchargé avec succès dans le répertoire : {current_directory}')
else:
    print('Échec du téléchargement du fichier.')