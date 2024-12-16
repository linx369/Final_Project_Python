from typing import List, Dict, Any
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    mean_absolute_percentage_error,
)
import polars as pl
import pandas as pd
import numpy as np


class HousePricePredictor:
    def __init__(self, train_data_path: str, test_data_path: str):
        """
        Initialize the predictor class with paths to the training and testing datasets.
        """
        self.train_data = pl.read_csv(str(train_data_path))
        self.test_data = pl.read_csv(str(test_data_path))
        self.models = {}  # Store trained models here


    def prepare_features(
        self, target_column: str = "SalePrice", selected_predictors: List[str] = None
    ):
        """
        Prepare the dataset for machine learning.
        """
        df = self.train_data.to_pandas()  # Convert to pandas for compatibility with sklearn
        X = df.drop(columns=[target_column]) if selected_predictors is None else df[selected_predictors]
        y = df[target_column]


        numeric_features = X.select_dtypes(include=["int64", "float64"]).columns
        categorical_features = X.select_dtypes(include=["object"]).columns


        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="mean")),
            ("scaler", StandardScaler())
        ])
        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("onehot", OneHotEncoder(handle_unknown="ignore"))
        ])


        preprocessor = ColumnTransformer(
            transformers=[
                ("num", numeric_transformer, numeric_features),
                ("cat", categorical_transformer, categorical_features)
            ]
        )


        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


        self.X_train = preprocessor.fit_transform(X_train)
        self.X_test = preprocessor.transform(X_test)
        self.y_train, self.y_test = y_train, y_test


    def train_baseline_models(self) -> Dict[str, Dict[str, float]]:
        """
        Train and evaluate baseline machine learning models for house price prediction.
        """
        results = {}


        models = {
            "Linear Regression": LinearRegression(),
            "Random Forest Regressor": RandomForestRegressor(random_state=42)
        }


        for name, model in models.items():
            model.fit(self.X_train, self.y_train)
            self.models[name] = model


            train_preds = model.predict(self.X_train)
            test_preds = model.predict(self.X_test)


            results[name] = {
                "metrics": {
                    "Train MSE": mean_squared_error(self.y_train, train_preds),
                    "Test MSE": mean_squared_error(self.y_test, test_preds),
                    "Train R2": r2_score(self.y_train, train_preds),
                    "Test R2": r2_score(self.y_test, test_preds),
                    "Train MAE": mean_absolute_error(self.y_train, train_preds),
                    "Test MAE": mean_absolute_error(self.y_test, test_preds),
                    "Train MAPE": mean_absolute_percentage_error(self.y_train, train_preds),
                    "Test MAPE": mean_absolute_percentage_error(self.y_test, test_preds),
                },
                "model": model
            }


        return results


    def forecast_sales_price(self, model_type: str = "Linear Regression"):
        """
        Use the trained model to forecast house prices on the test dataset.
        """
        if model_type not in self.models:
            raise ValueError(f"Model {model_type} is not trained.")


        test_df = self.test_data.to_pandas()
        test_features = test_df.drop(columns=["Id"])
        preprocessed_features = self.X_train.transform(test_features)
        predictions = self.models[model_type].predict(preprocessed_features)


        submission = pd.DataFrame({"Id": test_df["Id"], "SalePrice": predictions})
        output_folder = "src/real_estate_toolkit/ml_models/outputs/"
        os.makedirs(output_folder, exist_ok=True)
        submission_path = os.path.join(output_folder, "submission.csv")
        submission.to_csv(submission_path, index=False)


        print(f"Submission file saved to: {submission_path}")