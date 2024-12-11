import os
import pandas as pd
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt

# Define the directory where the CSV files will be downloaded
output_dir = os.path.dirname(os.path.abspath(__file__))

# Ensure the directory exists; create it if it doesn't
os.makedirs(output_dir, exist_ok=True)

# Set Kaggle configuration directory
os.environ['KAGGLE_CONFIG_DIR'] = os.path.expanduser("~/.kaggle")


def download_kaggle_dataset():
    """
    Downloads a specific dataset from Kaggle using the Kaggle API.
    The dataset is extracted into the defined output directory.

    Inputs:
    - None

    Outputs:
    - None: Files are downloaded and extracted directly into the output directory.
    """
    dataset_identifier = "davidcariboo/player-scores"
    
    # Use the Kaggle command-line tool to download and unzip the dataset
    os.system(f"kaggle datasets download -d {dataset_identifier} -p {output_dir} --unzip")
    print("Dataset download complete.")


def load_csv_data(file_name):
    """
    Loads a CSV file into a Pandas DataFrame.

    Inputs:
    - file_name (str): The name of the CSV file to be loaded.

    Outputs:
    - DataFrame: The loaded data if the file exists.
    - None: If the file does not exist, returns None and prints a warning message.
    """
    file_path = os.path.join(output_dir, file_name)
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        print(f"File not found: {file_name}")
        return None


# Decide whether to download the dataset or assume it's already downloaded
already_downloaded = True
if not already_downloaded:
    download_kaggle_dataset()

# Load the CSV data into DataFrames
players_df = load_csv_data("players.csv")
transfers_df = load_csv_data("transfers.csv")
valuations_df = load_csv_data("player_valuations.csv")
clubs_df = load_csv_data("clubs.csv")


# Filter transfers where the transfer fee is at least 100,000 and in the previous ten seasons
relevant_transfers = transfers_df[
    (transfers_df["transfer_fee"] >= 100000) &
    (transfers_df["transfer_season"].isin(["14/15", "15/16", "16/17", "17/18", "18/19", "20/21", "21/22", "22/23", "23/24", "24/25"]))
]

# Define the top 7 UEFA league IDs
top_7_uefa_leagues = ["GB1", "ES1", "IT1", "L1", "FR1", "PT1", "NL1"]

# Filter clubs that are in the top 7 leagues
top_clubs = clubs_df[clubs_df["domestic_competition_id"].isin(top_7_uefa_leagues)]

# Print the shape before the merge
print("Before Merge:", relevant_transfers.shape)

# Merge relevant transfers with the top_clubs data on 'club_id' for both 'from' and 'to' clubs
relevant_transfers = relevant_transfers.merge(
    top_clubs[['club_id', 'domestic_competition_id']],  # Only keeping the necessary columns
    left_on='from_club_id',  # Merge using the 'from_club_id' column
    right_on='club_id',  # Match with the 'club_id' column in top_clubs
    how='inner'
).merge(
    top_clubs[['club_id', 'domestic_competition_id']],  # Only keeping the necessary columns
    left_on='to_club_id',  # Merge using the 'to_club_id' column
    right_on='club_id',  # Match with the 'club_id' column in top_clubs
    how='inner',
    suffixes=('_from', '_to')  # Add suffixes to distinguish columns from both sides
)

# Drop unnecessary columns introduced by the merge
relevant_transfers.drop(columns=['club_id_from', 'club_id_to'], inplace=True)

# Rename columns for clarity, if needed
relevant_transfers.rename(
    columns={
        'domestic_competition_id_from': 'from_domestic_competition_id',
        'domestic_competition_id_to': 'to_domestic_competition_id'
    },
    inplace=True
)

# Print the shape after the merge
print("After Merge:", relevant_transfers.shape)

# Print the first few rows to check the result
print(relevant_transfers.head())





def calculate_mean_difference(df, col1, col2):
    """
    Calculates the absolute difference in means between two columns of a DataFrame.

    Inputs:
    - df (DataFrame): The DataFrame containing the data.
    - col1 (str): The first column name.
    - col2 (str): The second column name.

    Outputs:
    - float: The absolute difference between the means of the two columns.
    """
    return abs(df[col1].mean() - df[col2].mean())


def calculate_l1_distance(df, col1, col2):
    """
    Calculates the mean absolute error (L1 distance) between two columns of a DataFrame.

    Inputs:
    - df (DataFrame): The DataFrame containing the data.
    - col1 (str): The first column name.
    - col2 (str): The second column name.

    Outputs:
    - float: The mean absolute error between the two columns.
    """
    return (abs(df[col1] - df[col2])).mean()


def calculate_l2_distance(df, col1, col2):
    """
    Calculates the root mean squared error (L2 distance) between two columns of a DataFrame.

    Inputs:
    - df (DataFrame): The DataFrame containing the data.
    - col1 (str): The first column name.
    - col2 (str): The second column name.

    Outputs:
    - float: The root mean squared error between the two columns.
    """
    return sqrt(((df[col1] - df[col2])**2).sum())


def analyze_value_discrepancy(df, col1, col2):
    """
    Analyzes and prints statistical differences between two columns in a DataFrame.
    This includes mean, variance, absolute mean difference, mean absolute error (L1), and root mean squared error (L2).

    Inputs:
    - df (DataFrame): The DataFrame containing the data.
    - col1 (str): The first column name.
    - col2 (str): The second column name.

    Outputs:
    - None: Prints analysis results directly to the console.
    """
    print(f"Analysis for columns: {col1} vs {col2}")
    print(f"{col1} - Mean: {df[col1].mean()}, Variance: {df[col1].var()}")
    print(f"{col2} - Mean: {df[col2].mean()}, Variance: {df[col2].var()}")
    print(f"Absolute difference of means: {round(calculate_mean_difference(df, col1, col2))}")
    print(f"Mean absolute error (L1 distance): {round(calculate_l1_distance(df, col1, col2))}")
    print(f"Root mean squared error (L2 distance): {round(calculate_l2_distance(df, col1, col2))}")


# Analyze discrepancies between transfer fees and market values in the filtered dataset
analyze_value_discrepancy(relevant_transfers, "transfer_fee", "market_value_in_eur")



def calculate_club_metrics(df, club_col):
    """
    Calculate various metrics to evaluate a club's alignment with Transfermarkt values.

    Inputs:
    - df (DataFrame): DataFrame containing transfer data
    - club_col (str): Column name to group by (e.g., "from_club_name" or "to_club_name")

    Outputs:
    - DataFrame: Club-level metrics including correlation, mean ratio, RMSE, and APE.
    """
    club_metrics = []
    
    for club, group in df.groupby(club_col):
        # Filter to ensure sufficient data points
        if len(group) < 5:
            continue  # Skip clubs with fewer than 5 transactions
        
        # Metrics
        corr = group['transfer_fee'].corr(group['market_value_in_eur'])
        if pd.isna(corr):
            corr = 0  # Assign a default value
        ratio = group['transfer_fee'] / group['market_value_in_eur']
        mean_ratio = ratio.mean()
        ratio_std = ratio.std()
        rmse = np.sqrt(((group['transfer_fee'] - group['market_value_in_eur'])**2).mean())
        ape = (abs(group['transfer_fee'] - group['market_value_in_eur']) / group['market_value_in_eur']).mean()
        
        club_metrics.append({
            'club': club,
            'correlation': corr,
            'mean_ratio': mean_ratio,
            'ratio_std_dev': ratio_std,
            'rmse': rmse,
            'mean_ape': ape
        })
    
    return pd.DataFrame(club_metrics)

# Calculate metrics for clubs as sellers and buyers
seller_metrics = calculate_club_metrics(relevant_transfers, 'from_club_name')
buyer_metrics = calculate_club_metrics(relevant_transfers, 'to_club_name')

# Sort by correlation (or another metric of interest)
seller_metrics = seller_metrics.sort_values(by='correlation', ascending=False)
buyer_metrics = buyer_metrics.sort_values(by='correlation', ascending=False)
print(seller_metrics.head())
print(buyer_metrics.head())


# Trouver les clubs communs
common_clubs = set(seller_metrics['club']).intersection(set(buyer_metrics['club']))

# Filtrer les DataFrames pour ne garder que les clubs communs
seller_metrics_common = seller_metrics[seller_metrics['club'].isin(common_clubs)]
buyer_metrics_common = buyer_metrics[buyer_metrics['club'].isin(common_clubs)]

# Aligner les DataFrames pour garantir le même ordre
seller_metrics_common = seller_metrics_common.sort_values(by='club').reset_index(drop=True)
buyer_metrics_common = buyer_metrics_common.sort_values(by='club').reset_index(drop=True)

# Vérification des tailles
assert len(seller_metrics_common) == len(buyer_metrics_common), "Les tailles des DataFrames ne correspondent pas après le filtrage."

# Tracer le graphique
plt.figure(figsize=(8, 6))
plt.scatter(seller_metrics_common['correlation'], buyer_metrics_common['correlation'], alpha=0.7, edgecolor='k')
plt.xlabel("Seller Correlation (Transfer Fee vs Market Value)")
plt.ylabel("Buyer Correlation (Transfer Fee vs Market Value)")
plt.title("Correlation Between Transfer Values and Market Values")
plt.grid(True)
plt.savefig("output_graph.png")  # Sauvegarde le graphique
plt.show()
