import os
import pandas as pd
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from typing import Dict, List, Union
import logging 
from scipy.stats import pearsonr, spearmanr


def define_output_directory():
    """
    Defines the directory where the CSV files will be downloaded.
    Ensures that the directory exists by creating it if necessary.

    Returns:
    - str: The absolute path of the output directory.
    """
    output_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(output_dir, exist_ok=True)
    return output_dir

def configure_kaggle():
    """
    Configures the Kaggle API by setting the required environment variable.

    Returns:
    - None
    """
    os.environ['KAGGLE_CONFIG_DIR'] = os.path.expanduser("~/.kaggle")

def download_kaggle_dataset(output_dir):
    """
    Downloads a specific dataset from Kaggle using the Kaggle API.
    The dataset is extracted into the specified output directory.

    Inputs:
    - output_dir (str): Directory where the dataset will be extracted.

    Outputs:
    - None
    """
    dataset_identifier = "davidcariboo/player-scores"
    os.system(f"kaggle datasets download -d {dataset_identifier} -p {output_dir} --unzip")
    print("Dataset download complete.")

def load_csv_data(file_name, output_dir):
    """
    Loads a CSV file into a Pandas DataFrame.

    Inputs:
    - file_name (str): The name of the CSV file to be loaded.
    - output_dir (str): The directory where the file is located.

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

def filter_relevant_transfers(transfers_df):
    """
    Filters transfers where the transfer fee is at least 100,000 and occurred in the last ten seasons.

    Inputs:
    - transfers_df (DataFrame): The DataFrame containing transfer data.

    Outputs:
    - DataFrame: Filtered transfers.
    """
    recent_seasons = ["14/15", "15/16", "16/17", "17/18", "18/19", "20/21", "21/22", "22/23", "23/24", "24/25"]
    return transfers_df[
        (transfers_df["transfer_fee"] >= 100000) &
        (transfers_df["transfer_season"].isin(recent_seasons))
    ]

def filter_top_clubs(clubs_df):
    """
    Filters clubs that belong to the top 7 UEFA leagues.

    Inputs:
    - clubs_df (DataFrame): The DataFrame containing club data.

    Outputs:
    - DataFrame: Filtered clubs in top leagues.
    """
    top_7_uefa_leagues = ["GB1", "ES1", "IT1", "L1", "FR1", "PT1", "NL1"]
    return clubs_df[clubs_df["domestic_competition_id"].isin(top_7_uefa_leagues)]

def merge_transfers_with_clubs(transfers_df, clubs_df):
    """
    Merges transfer data with club data to include domestic competition information for both 'from' and 'to' clubs.

    Inputs:
    - transfers_df (DataFrame): The transfer data.
    - clubs_df (DataFrame): The club data.

    Outputs:
    - DataFrame: Merged transfers with club competition data.
    """
    merged = transfers_df.merge(
        clubs_df[['club_id', 'domestic_competition_id']],
        left_on='from_club_id',
        right_on='club_id',
        how='inner'
    ).merge(
        clubs_df[['club_id', 'domestic_competition_id']],
        left_on='to_club_id',
        right_on='club_id',
        how='inner',
        suffixes=('_from', '_to')
    )

    merged.drop(columns=['club_id_from', 'club_id_to'], inplace=True)
    merged.rename(
        columns={
            'domestic_competition_id_from': 'from_domestic_competition_id',
            'domestic_competition_id_to': 'to_domestic_competition_id'
        },
        inplace=True
    )
    return merged

def compute_correlations(x: Union[pd.Series, np.ndarray], y: Union[pd.Series, np.ndarray]) -> Dict[str, float]:
    """
    Computes Pearson and Spearman correlation coefficients between two variables.

    Inputs:
    - x (array-like): First variable.
    - y (array-like): Second variable.

    Outputs:
    - dict: Correlation coefficients (Pearson and Spearman) and associated p-values.
    """
    try:
        if isinstance(x, pd.Series):
            x = x.values
        if isinstance(y, pd.Series):
            y = y.values

        mask = ~np.isnan(x) & ~np.isnan(y)
        x_clean = x[mask]
        y_clean = y[mask]

        if len(x_clean) < 2 or len(y_clean) < 2:
            logging.warning(f"Not enough valid data points to compute correlations. Only {len(x_clean)} valid data points found.")
            return {}

        if np.all(x_clean == x_clean[0]) or np.all(y_clean == y_clean[0]):
            logging.warning("An input array is constant; the correlation coefficient is not defined.")
            return {}

        pearson_corr, pearson_p = pearsonr(x_clean, y_clean)
        spearman_corr, spearman_p = spearmanr(x_clean, y_clean)
        return {
            "Pearson_correlation": float(pearson_corr),
            "Pearson_p_value": float(pearson_p),
            "Spearman_correlation": float(spearman_corr),
            "Spearman_p_value": float(spearman_p)
        }
    except Exception as e:
        logging.error(f"Error computing correlations: {e}")
        return {}

def calculate_statistical_distances(df, col1, col2):
    """
    Calculates mean absolute error (L1), root mean squared error (L2), and absolute mean difference between two columns.

    Inputs:
    - df (DataFrame): The DataFrame containing the data.
    - col1 (str): The first column name.
    - col2 (str): The second column name.

    Outputs:
    - dict: Dictionary containing the calculated distances.
    """
    l1_distance = (abs(df[col1] - df[col2])).mean()
    l2_distance = sqrt(((df[col1] - df[col2])**2).sum())
    mean_difference = abs(df[col1].mean() - df[col2].mean())
    return {
        "L1_distance": l1_distance,
        "L2_distance": l2_distance,
        "Mean_difference": mean_difference
    }

def analyze_value_discrepancy(df, col1, col2):
    """
    Prints statistical differences between two columns in a DataFrame.

    Inputs:
    - df (DataFrame): The DataFrame containing the data.
    - col1 (str): The first column name.
    - col2 (str): The second column name.

    Outputs:
    - None
    """
    stats = calculate_statistical_distances(df, col1, col2)
    print(f"Analysis for columns: {col1} vs {col2}")
    print(f"Mean Difference: {stats['Mean_difference']}")
    print(f"L1 Distance: {stats['L1_distance']}")
    print(f"L2 Distance: {stats['L2_distance']}")

def align_dataframes_by_club(seller_metrics, buyer_metrics):
    """
    Aligns seller and buyer DataFrames to ensure both are sorted by club in the same order.

    Inputs:
    - seller_metrics (DataFrame): DataFrame of seller metrics.
    - buyer_metrics (DataFrame): DataFrame of buyer metrics.

    Outputs:
    - tuple: Two DataFrames sorted by club.
    """
    seller_metrics_common = seller_metrics.sort_values(by='club').reset_index(drop=True)
    buyer_metrics_common = buyer_metrics.sort_values(by='club').reset_index(drop=True)
    return seller_metrics_common, buyer_metrics_common

def plot_comparative_metrics(seller_metrics_common, buyer_metrics_common):
    """
    Plots comparative metrics between seller and buyer statistics.

    Inputs:
    - seller_metrics_common (DataFrame): Aligned seller metrics DataFrame.
    - buyer_metrics_common (DataFrame): Aligned buyer metrics DataFrame.

    Outputs:
    - None
    """
    plt.figure(figsize=(10, 6))
    plt.scatter(seller_metrics_common['correlation'], buyer_metrics_common['correlation'])

    # Afficher les noms des clubs avec les valeurs de corrélation les plus basses et les plus hautes
    num_labels =  4 # Nombre de labels à afficher pour chaque extrême
    indices_to_label = (
        seller_metrics_common['correlation'].nsmallest(num_labels).index.tolist() +
        seller_metrics_common['correlation'].nlargest(num_labels).index.tolist() +
        buyer_metrics_common['correlation'].nsmallest(num_labels).index.tolist() +
        buyer_metrics_common['correlation'].nlargest(num_labels).index.tolist()
    )
    indices_to_label = list(set(indices_to_label))  # Éviter les doublons

    for i in indices_to_label:
        if np.isfinite(seller_metrics_common.loc[i, 'correlation']) and np.isfinite(buyer_metrics_common.loc[i, 'correlation']):
            plt.text(seller_metrics_common.loc[i, 'correlation'], buyer_metrics_common.loc[i, 'correlation'], seller_metrics_common.loc[i, 'club'], fontsize=9)

    plt.xlabel('Pearson Correlation (Seller)')
    plt.ylabel('Pearson Correlation (Buyer)')
    plt.title('Pearson Correlation of Transfer Fees vs Market Values by Club')
    plt.grid(True)
    plt.show()

def calculate_club_metrics(transfers_df, club_column):
    """
    Calculate Pearson correlation metrics for clubs based on transfer data.

    Inputs:
    - transfers_df (DataFrame): DataFrame containing transfer data.
    - club_column (str): Column name indicating the club (either 'from_club_name' or 'to_club_name').

    Outputs:
    - DataFrame: DataFrame containing club metrics.
    """
    club_metrics = []

    for club in transfers_df[club_column].unique():
        club_transfers = transfers_df[transfers_df[club_column] == club]
        if len(club_transfers) < 5:
            logging.warning(f"Not enough valid data points for club {club}. Skipping.")
            correlation = np.nan
        else:
            correlations = compute_correlations(club_transfers['transfer_fee'], club_transfers['market_value_in_eur'])
            correlation = correlations.get('Pearson_correlation', np.nan)

        club_metrics.append({
            'club': club,
            'correlation': correlation
        })

    return pd.DataFrame(club_metrics)

def analyze_club_metrics(relevant_transfers):
    """
    Analyze and plot comparative metrics for clubs as sellers and buyers.

    Inputs:
    - relevant_transfers (DataFrame): DataFrame containing relevant transfer data.

    Outputs:
    - None
    """
    # Calculate metrics for clubs as sellers and buyers
    seller_metrics = calculate_club_metrics(relevant_transfers, 'from_club_name')
    buyer_metrics = calculate_club_metrics(relevant_transfers, 'to_club_name')

    # Sort by correlation (or another metric of interest)
    seller_metrics = seller_metrics.sort_values(by='correlation', ascending=False)
    buyer_metrics = buyer_metrics.sort_values(by='correlation', ascending=False)
    print(seller_metrics.head())
    print(buyer_metrics.head())

    # Find common clubs
    common_clubs = set(seller_metrics['club']).intersection(set(buyer_metrics['club']))

    # Filter DataFrames to keep only common clubs
    seller_metrics_common = seller_metrics[seller_metrics['club'].isin(common_clubs)]
    buyer_metrics_common = buyer_metrics[buyer_metrics['club'].isin(common_clubs)]

    # Align DataFrames to ensure the same order
    seller_metrics_common, buyer_metrics_common = align_dataframes_by_club(seller_metrics_common, buyer_metrics_common)

    # Plot comparative metrics
    plot_comparative_metrics(seller_metrics_common, buyer_metrics_common)

def main():
    """
    Main function to orchestrate data loading, processing, and analysis.

    Inputs:
    - None

    Outputs:
    - None
    """
    output_dir = define_output_directory()
    configure_kaggle()

    # Uncomment to download the dataset if needed
    # download_kaggle_dataset(output_dir)

    players_df = load_csv_data("players.csv", output_dir)
    transfers_df = load_csv_data("transfers.csv", output_dir)
    valuations_df = load_csv_data("player_valuations.csv", output_dir)
    clubs_df = load_csv_data("clubs.csv", output_dir)

    relevant_transfers = filter_relevant_transfers(transfers_df)
    top_clubs = filter_top_clubs(clubs_df)
    relevant_transfers = merge_transfers_with_clubs(relevant_transfers, top_clubs)

    analyze_value_discrepancy(relevant_transfers, "transfer_fee", "market_value_in_eur")
