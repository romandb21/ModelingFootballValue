import os
import pandas as pd
from math import sqrt
# Définir le chemin du dossier où les fichiers CSV doivent être téléchargés
output_dir = "/home/onyxia/work/ModelingFootballValue"

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


already_downloaded = True
if already_downloaded is False:
    download_kaggle_dataset()
players = load_data("/home/onyxia/work/ModelingFootballValue/players.csv")
transfers = load_data("/home/onyxia/work/ModelingFootballValue/transfers.csv")
valuations = load_data("/home/onyxia/work/ModelingFootballValue/player_valuations.csv")

     
# Select only relevant transfers

transfers_rel = transfers[transfers["transfer_fee"] >= 100000]

# Differences between transfermarkt market values and transfer fees


def diff_mean(df, v1, v2):
    return abs(df[v1].mean() - df[v2].mean())


def dist_l1(df, v1, v2):
    return (abs(df[v1] - df[v2])).mean()


def dist_l2(df, v1, v2):
    return sqrt(((df[v1] - df[v2])**2).sum())


def diff_distribution(df, v1, v2):
    print(v1, "mean is", str(df[v1].mean()), "and variance is", str(df[v1].var()))
    print(v2, "mean is", str(df[v2].mean()), "and variance is", str(df[v2].var()))
    print("Absolute difference of their means is", str(diff_mean(df, v1, v2)), ", the mean absolute error is", str(dist_l1(df, v1, v2)), "and the root mean squared error is", str(dist_l2(df, v1, v2)))


diff_distribution(transfers_rel, "transfer_fee", "market_value_in_eur")