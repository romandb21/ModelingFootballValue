import os
import pandas as pd
import numpy as np
from math import sqrt
import matplotlib.pyplot as plt
from scipy.stats import pearsonr, spearmanr
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import logging
from typing import Dict, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to compute Pearson and Spearman correlations between two variables
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
        pearson_corr, pearson_p = pearsonr(x, y)
        spearman_corr, spearman_p = spearmanr(x, y)
        return {
            "Pearson_correlation": float(pearson_corr),
            "Pearson_p_value": float(pearson_p),
            "Spearman_correlation": float(spearman_corr),
            "Spearman_p_value": float(spearman_p)
        }
    except Exception as e:
        logging.error(f"Error computing correlations: {e}")
        return {}

# Function to perform a linear regression
def linear_regression(X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray]) -> Dict[str, Union[List[float], float]]:
    """
    Performs a linear regression between a target variable and explanatory variables.

    Inputs:
    - X (DataFrame or array-like): Explanatory variables.
    - y (array-like): Target variable.

    Outputs:
    - dict: Regression coefficients and performance metrics (MSE and RMSE).
    """
    try:
        model = LinearRegression()
        model.fit(X, y)
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        rmse = sqrt(mse)
        return {
            "Coefficients": model.coef_.tolist(),
            "Intercept": float(model.intercept_),
            "MSE": float(mse),
            "RMSE": float(rmse)
        }
    except Exception as e:
        logging.error(f"Error performing linear regression: {e}")
        return {}

# Function to perform a Lasso regression
def lasso_regression(X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], alpha: float = 1.0) -> Dict[str, Union[List[float], float]]:
    """
    Performs a Lasso regression between a target variable and explanatory variables.

    Inputs:
    - X (DataFrame or array-like): Explanatory variables.
    - y (array-like): Target variable.
    - alpha (float): Regularization parameter for Lasso.

    Outputs:
    - dict: Regression coefficients and performance metrics (MSE and RMSE).
    """
    try:
        model = Lasso(alpha=alpha)
        model.fit(X, y)
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        rmse = sqrt(mse)
        return {
            "Coefficients": model.coef_.tolist(),
            "Intercept": float(model.intercept_),
            "MSE": float(mse),
            "RMSE": float(rmse)
        }
    except Exception as e:
        logging.error(f"Error performing Lasso regression: {e}")
        return {}

# Function to plot a regression and the scatter plot
def plot_regression(X: np.ndarray, y: np.ndarray, model: Union[LinearRegression, Lasso], feature_name: str, target_name: str) -> None:
    """
    Plots a regression and the scatter plot of observed data.

    Inputs:
    - X (array-like): Explanatory variables used for the regression (one variable for the plot).
    - y (array-like): Target variable.
    - model: Trained regression model.
    - feature_name (str): Name of the explanatory variable for the x-axis.
    - target_name (str): Name of the target variable for the y-axis.

    Outputs:
    - None
    """
    if X.shape[1] != 1:
        raise ValueError("This function only supports regressions with one explanatory variable for plotting.")

    try:
        X = X.flatten()
        y_pred = model.predict(X.reshape(-1, 1))

        plt.figure(figsize=(8, 6))
        plt.scatter(X, y, alpha=0.7, label="Observations")
        plt.plot(X, y_pred, color='red', linewidth=2, label="Regression")
        plt.xlabel(feature_name)
        plt.ylabel(target_name)
        plt.title(f"Regression between {feature_name} and {target_name}")
        plt.legend()
        plt.grid(True)
        plt.show()
    except Exception as e:
        logging.error(f"Error plotting regression: {e}")

# Function to perform a random forest regression
def random_forest_regression(X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], n_estimators: int = 100, max_depth: int = None) -> Dict[str, Union[List[float], float]]:
    """
    Performs a random forest regression between a target variable and explanatory variables.

    Inputs:
    - X (DataFrame or array-like): Explanatory variables.
    - y (array-like): Target variable.
    - n_estimators (int): Number of trees in the forest.
    - max_depth (int): Maximum depth of the trees.

    Outputs:
    - dict: Regression coefficients and performance metrics (MSE and RMSE).
    """
    try:
        model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth)
        model.fit(X, y)
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        rmse = sqrt(mse)
        return {
            "Feature_importances": model.feature_importances_.tolist(),
            "MSE": float(mse),
            "RMSE": float(rmse)
        }
    except Exception as e:
        logging.error(f"Error performing random forest regression: {e}")
        return {}

# Function to plot the feature importances of a random forest model
def plot_rf_feature_importances(importances: Union[np.ndarray, List[float]], feature_names: List[str]) -> None:
    """
    Plots the feature importances of a random forest model.

    Inputs:
    - importances (array-like): Feature importances.
    - feature_names (list): Names of the features.

    Outputs:
    - None
    """
    try:
        importances = np.array(importances)  # Convert to numpy array
        indices = np.argsort(importances)[::-1]

        plt.figure(figsize=(8, 6))
        plt.bar(range(len(importances)), importances[indices], align='center')
        plt.xticks(range(len(importances)), np.array(feature_names)[indices], rotation=90)
        plt.xlabel("Feature")
        plt.ylabel("Importance")
        plt.title("Random Forest Feature Importances")
        plt.grid(True)
        plt.show()
    except Exception as e:
        logging.error(f"Error plotting random forest feature importances: {e}")

# Function to perform an XGBoost regression
def xgboost_regression(X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], n_estimators: int = 100, max_depth: int = 3, learning_rate: float = 0.1) -> Dict[str, Union[List[float], float]]:
    """
    Performs an XGBoost regression between a target variable and explanatory variables.

    Inputs:
    - X (DataFrame or array-like): Explanatory variables.
    - y (array-like): Target variable.
    - n_estimators (int): Number of boosting rounds.
    - max_depth (int): Maximum depth of the trees.
    - learning_rate (float): Step size shrinkage used in update to prevent overfitting.

    Outputs:
    - dict: Regression coefficients and performance metrics (MSE and RMSE).
    """
    try:
        model = XGBRegressor(n_estimators=n_estimators, max_depth=max_depth, learning_rate=learning_rate)
        model.fit(X, y)
        y_pred = model.predict(X)
        mse = mean_squared_error(y, y_pred)
        rmse = sqrt(mse)
        return {
            "Feature_importances": model.feature_importances_.tolist(),
            "MSE": float(mse),
            "RMSE": float(rmse)
        }
    except Exception as e:
        logging.error(f"Error performing XGBoost regression: {e}")
        return {}

# Function to plot the feature importances of an XGBoost model
def plot_xgb_feature_importances(importances: Union[np.ndarray, List[float]], feature_names: List[str]) -> None:
    """
    Plots the feature importances of an XGBoost model.

    Inputs:
    - importances (array-like): Feature importances.
    - feature_names (list): Names of the features.

    Outputs:
    - None
    """
    try:
        importances = np.array(importances)  # Convert to numpy array
        indices = np.argsort(importances)[::-1]

        plt.figure(figsize=(8, 6))
        plt.bar(range(len(importances)), importances[indices], align='center')
        plt.xticks(range(len(importances)), np.array(feature_names)[indices], rotation=90)
        plt.xlabel("Feature")
        plt.ylabel("Importance")
        plt.title("XGBoost Feature Importances")
        plt.grid(True)
        plt.show()
    except Exception as e:
        logging.error(f"Error plotting XGBoost feature importances: {e}")

