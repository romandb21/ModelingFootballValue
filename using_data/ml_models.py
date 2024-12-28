import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression, Lasso
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
import logging
from typing import Dict, List, Union
from sklearn.model_selection import train_test_split

def linear_regression(X: np.ndarray, y: np.ndarray, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Union[np.ndarray, float, np.ndarray]]:
    """
    Performs linear regression, returns the predictions, mean squared error, R^2, and coefficients.

    Inputs:
    - X (array-like): Explanatory variables.
    - y (array-like): Target variable.
    - test_size (float): Proportion of the dataset to include in the test split.
    - random_state (int): Random seed for reproducibility.

    Outputs:
    - dict: Dictionary containing predictions, mean squared error, R^2, and coefficients.
    """
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        model = LinearRegression()
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        r2_train = model.score(X_train, y_train)
        r2_test = model.score(X_test, y_test)
        coefficients = model.coef_
        return {
            "model": model,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
            "mse_train": mse_train,
            "mse_test": mse_test,
            "r2_train": r2_train,
            "r2_test": r2_test,
            "coefficients": coefficients
        }
    except Exception as e:
        logging.error(f"Error performing linear regression: {e}")
        return {}

def lasso_regression(X: np.ndarray, y: np.ndarray, alpha: float = 1.0, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Union[np.ndarray, float, np.ndarray]]:
    """
    Performs Lasso regression, returns the predictions, mean squared error, R^2, and coefficients.

    Inputs:
    - X (array-like): Explanatory variables.
    - y (array-like): Target variable.
    - alpha (float): Regularization strength.
    - test_size (float): Proportion of the dataset to include in the test split.
    - random_state (int): Random seed for reproducibility.

    Outputs:
    - dict: Dictionary containing predictions, mean squared error, R^2, and coefficients.
    """
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        model = Lasso(alpha=alpha)
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        r2_train = model.score(X_train, y_train)
        r2_test = model.score(X_test, y_test)
        coefficients = model.coef_
        return {
            "model": model,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
            "mse_train": mse_train,
            "mse_test": mse_test,
            "r2_train": r2_train,
            "r2_test": r2_test,
            "coefficients": coefficients
        }
    except Exception as e:
        logging.error(f"Error performing Lasso regression: {e}")
        return {}

def plot_regression(X: np.ndarray, y: np.ndarray, regression_result: Dict[str, Union[np.ndarray, float]], feature_name: str, target_name: str) -> None:
    """
    Plots a regression and the scatter plot of observed data.

    Inputs:
    - X (array-like): Explanatory variables used for the regression (one variable for the plot).
    - y (array-like): Target variable.
    - regression_result: Dictionary containing the trained model and predictions.
    - feature_name (str): Name of the explanatory variable for the x-axis.
    - target_name (str): Name of the target variable for the y-axis.

    Outputs:
    - None
    """
    if X.shape[1] != 1:
        raise ValueError("This function only supports regressions with one explanatory variable for plotting.")

    try:
        X = X.flatten()
        model = regression_result["model"]
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

def random_forest_regression(X: np.ndarray, y: np.ndarray, n_estimators: int = 100, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Union[np.ndarray, float, List[str]]]:
    """
    Performs Random Forest regression, returns the predictions, mean squared error, R^2, feature importances, and feature names.

    Inputs:
    - X (array-like): Explanatory variables.
    - y (array-like): Target variable.
    - n_estimators (int): Number of trees in the forest.
    - test_size (float): Proportion of the dataset to include in the test split.
    - random_state (int): Random seed for reproducibility.

    Outputs:
    - dict: Dictionary containing predictions, mean squared error, R^2, feature importances, and feature names.
    """
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        model = RandomForestRegressor(n_estimators=n_estimators, random_state=random_state)
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        r2_train = model.score(X_train, y_train)
        r2_test = model.score(X_test, y_test)
        feature_importances = model.feature_importances_
        feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else [f"Feature {i}" for i in range(X.shape[1])]
        return {
            "model": model,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
            "mse_train": mse_train,
            "mse_test": mse_test,
            "r2_train": r2_train,
            "r2_test": r2_test,
            "feature_importances": feature_importances,
            "feature_names": feature_names
        }
    except Exception as e:
        logging.error(f"Error performing Random Forest regression: {e}")
        return {}

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

def xgboost_regression(X: Union[pd.DataFrame, np.ndarray], y: Union[pd.Series, np.ndarray], n_estimators: int = 100, max_depth: int = 3, learning_rate: float = 0.1, test_size: float = 0.2, random_state: int = 42) -> Dict[str, Union[List[float], float, List[str]]]:
    """
    Performs an XGBoost regression, returns the predictions, mean squared error, R^2, and feature importances.

    Inputs:
    - X (DataFrame or array-like): Explanatory variables.
    - y (array-like): Target variable.
    - n_estimators (int): Number of boosting rounds.
    - max_depth (int): Maximum depth of the trees.
    - learning_rate (float): Step size shrinkage used in update to prevent overfitting.
    - test_size (float): Proportion of the dataset to include in the test split.
    - random_state (int): Random seed for reproducibility.

    Outputs:
    - dict: Dictionary containing predictions, mean squared error, R^2, and feature importances.
    """
    try:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
        model = XGBRegressor(n_estimators=n_estimators, max_depth=max_depth, learning_rate=learning_rate, random_state=random_state)
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        mse_train = mean_squared_error(y_train, y_pred_train)
        mse_test = mean_squared_error(y_test, y_pred_test)
        r2_train = model.score(X_train, y_train)
        r2_test = model.score(X_test, y_test)
        feature_importances = model.feature_importances_
        feature_names = X.columns.tolist() if isinstance(X, pd.DataFrame) else [f"Feature {i}" for i in range(X.shape[1])]
        return {
            "model": model,
            "y_pred_train": y_pred_train,
            "y_pred_test": y_pred_test,
            "mse_train": mse_train,
            "mse_test": mse_test,
            "r2_train": r2_train,
            "r2_test": r2_test,
            "feature_importances": feature_importances,
            "feature_names": feature_names
        }
    except Exception as e:
        logging.error(f"Error performing XGBoost regression: {e}")
        return {}

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

