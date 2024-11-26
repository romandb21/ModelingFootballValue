import os
import pandas as pd

# Définir le chemin du dossier où les fichiers CSV doivent être téléchargés
output_dir = "~/work/ModelingFootballValue"

# Assurez-vous que le répertoire existe, sinon créez-le
os.makedirs(output_dir, exist_ok=True)

# Assurez-vous que votre fichier kaggle.json est correctement configuré
os.environ['KAGGLE_CONFIG_DIR'] = os.path.expanduser("~/.kaggle")

# Télécharger les données depuis Kaggle
def download_kaggle_dataset():
    dataset_name = "davidcariboo/player-scores"
    
    # Téléchargement et extraction du fichier .zip dans le dossier spécifié
    os.system(f"kaggle datasets download -d {dataset_name} -p {output_dir} --unzip")
    print("Téléchargement terminé.")

# Charger les données dans un DataFrame
def load_data(file_name):
    file_path = os.path.join(output_dir, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"Le fichier {file_name} n'existe pas.")
        return None


# Téléchargement et chargement des données
download_kaggle_dataset()
players_df = load_data("/home/onyxia/work/ModelingFootballValue/players.csv")

if players_df is not None:
    print(players_df.head())
