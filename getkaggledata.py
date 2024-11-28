import os
import pandas as pd
import numpy as np
from math import sqrt

# Define the directory where the CSV files will be downloaded
output_dir = "/home/onyxia/work/ModelingFootballValue"

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

# Filter transfers where the transfer fee is at least 100,000 and in the previous ten seasons
relevant_transfers = transfers_df[
    (transfers_df["transfer_fee"] >= 100000) &
    (transfers_df["transfer_season"].isin(["14/15", "15/16", "16/17", "17/18", "18/19", "20/21", "21/22", "22/23", "23/24", "24/25"]))
]


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