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

# Fonction pour calculer la corrélation classique et de Spearman entre deux variables
def compute_correlations(x, y):
    """
    Calcule les coefficients de corrélation classique (Pearson) et Spearman entre deux variables.

    Inputs:
    - x (array-like): Première variable.
    - y (array-like): Deuxième variable.

    Outputs:
    - dict: Coefficients de corrélation (Pearson et Spearman) et p-values associées.
    """
    pearson_corr, pearson_p = pearsonr(x, y)
    spearman_corr, spearman_p = spearmanr(x, y)
    return {
        "Pearson_correlation": float(pearson_corr),
        "Pearson_p_value": float(pearson_p),
        "Spearman_correlation": float(spearman_corr),
        "Spearman_p_value": float(spearman_p)
    }

# Fonction pour effectuer une régression linéaire classique
def linear_regression(X, y):
    """
    Effectue une régression linéaire classique entre une variable cible et des variables explicatives.

    Inputs:
    - X (DataFrame or array-like): Variables explicatives.
    - y (array-like): Variable cible.

    Outputs:
    - dict: Coefficients de la régression et métriques de performance (MSE et RMSE).
    """
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

# Fonction pour effectuer une régression Lasso
def lasso_regression(X, y, alpha=1.0):
    """
    Effectue une régression Lasso entre une variable cible et des variables explicatives.

    Inputs:
    - X (DataFrame or array-like): Variables explicatives.
    - y (array-like): Variable cible.
    - alpha (float): Paramètre de régularisation pour Lasso.

    Outputs:
    - dict: Coefficients de la régression et métriques de performance (MSE et RMSE).
    """
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

# Fonction pour tracer une régression et le nuage de points
def plot_regression(X, y, model, feature_name, target_name):
    """
    Trace une régression et le nuage de points des données observées.

    Inputs:
    - X (array-like): Variables explicatives utilisées pour la régression (une seule variable pour le graphique).
    - y (array-like): Variable cible.
    - model: Modèle de régression entraîné.
    - feature_name (str): Nom de la variable explicative pour l'axe des x.
    - target_name (str): Nom de la variable cible pour l'axe des y.

    Outputs:
    - None
    """
    if X.shape[1] != 1:
        raise ValueError("Cette fonction ne supporte que les régressions avec une seule variable explicative pour le tracé.")

    X = X.flatten()
    y_pred = model.predict(X.reshape(-1, 1))

    plt.figure(figsize=(8, 6))
    plt.scatter(X, y, alpha=0.7, label="Observations")
    plt.plot(X, y_pred, color='red', linewidth=2, label="Régression")
    plt.xlabel(feature_name)
    plt.ylabel(target_name)
    plt.title(f"Régression entre {feature_name} et {target_name}")
    plt.legend()
    plt.grid(True)
    plt.show()

# Exemple d'utilisation
def main():
    # Exemple fictif
    X = np.random.rand(100, 1) * 100  # Une variable explicative
    y = 2.5 * X.flatten() + np.random.randn(100) * 10  # Variable cible avec bruit

    # Calcul des corrélations
    correlations = compute_correlations(X.flatten(), y)
    print("Corrélations:", correlations)

    # Régression linéaire
    lin_reg_results = linear_regression(X, y)
    print("Régression linéaire:", lin_reg_results)

    # Régression Lasso
    lasso_results = lasso_regression(X, y, alpha=0.1)
    print("Régression Lasso:", lasso_results)

    # Tracé des résultats
    model = LinearRegression()
    model.fit(X, y)
    plot_regression(X, y, model, feature_name="Variable Explicative", target_name="Variable Cible")

main()

# function that makes a random forest regression


def random_forest_regression(X, y, n_estimators=100, max_depth=None):
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


# function to plot the feature importances of a random forest model
def plot_rf_feature_importances(importances, feature_names):
    """
    Plots the feature importances of a random forest model.

    Inputs:
    - importances (array-like): Feature importances.
    - feature_names (list): Names of the features.

    Outputs:
    - None
    """
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

# function that makes a xgboost regression
def xgboost_regression(X, y, n_estimators=100, max_depth=3, learning_rate=0.1):
    """
    Performs a XGBoost regression between a target variable and explanatory variables.

    Inputs:
    - X (DataFrame or array-like): Explanatory variables.
    - y (array-like): Target variable.
    - n_estimators (int): Number of boosting rounds.
    - max_depth (int): Maximum depth of the trees.
    - learning_rate (float): Step size shrinkage used in update to prevent overfitting.

    Outputs:
    - dict: Regression coefficients and performance metrics (MSE and RMSE).
    """
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

# function to plot the feature importances of a xgboost model
def plot_xgb_feature_importances(importances, feature_names):
    """
    Plots the feature importances of a XGBoost model.

    Inputs:
    - importances (array-like): Feature importances.
    - feature_names (list): Names of the features.

    Outputs:
    - None
    """
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

# Exemple d'utilisation
def main():
    # Exemple fictif
    X = np.random.rand(100, 3) * 100  # Trois variables explicatives
    y = 2.5 * X[:, 0] + 1.5 * X[:, 1] - 3 * X[:, 2] + np.random.randn(100) * 10  # Variable cible avec bruit

    # Régression Random Forest
    rf_results = random_forest_regression(X, y, n_estimators=100, max_depth=None)
    print("Régression Random Forest:", rf_results)

    # Tracé des importances des variables explicatives
    plot_rf_feature_importances(rf_results["Feature_importances"], feature_names=["Var1", "Var2", "Var3"])

    # Régression XGBoost
    xgb_results = xgboost_regression(X, y, n_estimators=100, max_depth=3, learning_rate=0.1)

    # Tracé des importances des variables explicatives
    plot_xgb_feature_importances(xgb_results["Feature_importances"], feature_names=["Var1", "Var2", "Var3"])

main()
