import os
import zipfile

# Configuration de l'environnement pour utiliser le fichier kaggle.json local
# Cela évite d'avoir à le mettre dans le dossier système C:\Users\HP\.kaggle\
os.environ['KAGGLE_CONFIG_DIR'] = os.path.dirname(os.path.abspath(__file__))

print("Initialisation de l'API Kaggle...")
try:
    from kaggle.api.kaggle_api_extended import KaggleApi
    api = KaggleApi()
    api.authenticate()
    print("Authentification Kaggle réussie !")
except Exception as e:
    print(f"Erreur d'authentification. As-tu bien placé kaggle.json dans {os.environ['KAGGLE_CONFIG_DIR']} ?")
    print(f"Détail de l'erreur : {e}")
    exit(1)

# Dossier de destination des données
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Datasets à télécharger
DATASETS = {
    # Dataset d'URLs de Phishing (très utilisé sur Kaggle)
    'urls': 'taruntiwarihari/phishing-site-urls',
    # Dataset d'Emails Enron (Spam vs Ham)
    'emails': 'wcukierski/enron-email-dataset'
}

for name, dataset_name in DATASETS.items():
    print(f"\n--- Téléchargement du dataset {name} ({dataset_name}) ---")
    try:
        api.dataset_download_files(dataset_name, path=DATA_DIR, unzip=True)
        print(f"Dataset {name} téléchargé et décompressé avec succès dans {DATA_DIR} !")
    except Exception as e:
        print(f"Erreur lors du téléchargement du dataset {name}: {e}")

print("\nOpération terminée.")
