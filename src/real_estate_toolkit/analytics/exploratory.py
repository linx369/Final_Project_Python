import os
import plotly.express as px
import polars as pl
import pandas as pd
import plotly.graph_objects as go
from typing import List, Dict

class MarketAnalyzer:
    def __init__(self, data_path: str):
        """
        Initialize the analyzer with data from a CSV file.

        Args:
            data_path (str): Path to the Ames Housing dataset
        """
        self.data_path = data_path
        # Read CSV as Polars DataFrame
        self.real_state_data = pl.read_csv(str(self.data_path))
        self.real_state_clean_data = None  # Will store a cleaned Pandas DataFrame after clean_data() is called.

    def clean_data(self) -> None:
        """
        Perform comprehensive data cleaning.

        For now:
        - Convert the Polars DataFrame to a Pandas DataFrame.
        - Create a 'TotalSF' column if needed.
        """
        # Convert to Pandas
        self.real_state_clean_data = self.real_state_data.to_pandas()

        # If 'TotalSF' column is needed and doesn't exist, create it.
        # Assuming TotalSF = GrLivArea + TotalBsmtSF (as an example)
        if "GrLivArea" in self.real_state_clean_data.columns and "TotalBsmtSF" in self.real_state_clean_data.columns:
            self.real_state_clean_data["TotalSF"] = self.real_state_clean_data["GrLivArea"] + self.real_state_clean_data["TotalBsmtSF"]
        else:
            # If TotalBsmtSF isn't available, just duplicate GrLivArea for demonstration
            # Adjust this logic based on your actual dataset needs
            self.real_state_clean_data["TotalSF"] = self.real_state_clean_data["GrLivArea"]

    def generate_price_distribution_analysis(self) -> pl.DataFrame:
        """
        Analyze sale price distribution using clean data.

        Steps:
        1. Compute price statistics.
        2. Create a histogram of sale prices.

        Returns:
            Statistical insights Polars DataFrame
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data not cleaned. Call clean_data() before analysis.")

        # Compute statistics using Pandas
        sale_price = self.real_state_clean_data["SalePrice"]
        price_stats = {
            "mean": sale_price.mean(),
            "median": sale_price.median(),
            "std": sale_price.std(),
            "min": sale_price.min(),
            "max": sale_price.max()
        }

        price_stats_df = pd.DataFrame([price_stats])
        price_stats_pl = pl.from_pandas(price_stats_df)

        # Create histogram with Plotly
        fig = px.histogram(
            self.real_state_clean_data,
            x="SalePrice",
            nbins=50,
            title="Sale Price Distribution",
            labels={"SalePrice": "Sale Price"}
        )

        # Save figure
        output_folder = "src/real_estate_toolkit/analytics/outputs/"
        os.makedirs(output_folder, exist_ok=True)
        plot_file = os.path.join(output_folder, "price_distribution.html")
        fig.write_html(plot_file)
        print(f"Price distribution histogram saved to: {plot_file}")

        return price_stats_pl

    def neighborhood_price_comparison(self) -> pl.DataFrame:
        """
        Compare house prices by neighborhood.

        Returns:
            Polars DataFrame with neighborhood statistics
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data not cleaned. Call clean_data() before analysis.")

        output_folder = "src/real_estate_toolkit/analytics/outputs/"
        os.makedirs(output_folder, exist_ok=True)

        # Convert Pandas to Polars for computation
        polars_data = pl.from_pandas(self.real_state_clean_data)

        # Group by neighborhood
        neighborhood_stats = polars_data.groupby("Neighborhood").agg([
            pl.col("SalePrice").mean().alias("mean_price"),
            pl.col("SalePrice").median().alias("median_price"),
            pl.col("SalePrice").std().alias("std_dev_price"),
            pl.col("SalePrice").min().alias("min_price"),
            pl.col("SalePrice").max().alias("max_price")
        ])

        # Convert back to Pandas for Plotly
        neighborhood_stats_pandas = neighborhood_stats.to_pandas()

        # Create a boxplot for price comparison by neighborhood
        fig = px.box(
            self.real_state_clean_data,
            x="Neighborhood",
            y="SalePrice",
            color="Neighborhood",
            title="House Price Distribution by Neighborhood",
            labels={"Neighborhood": "Neighborhood", "SalePrice": "Sale Price"},
            points="all"
        )

        plot_file = os.path.join(output_folder, "neighborhood_price_comparison.html")
        fig.write_html(plot_file)
        print(f"Boxplot saved to: {plot_file}")

        return neighborhood_stats

    def feature_correlation_heatmap(self, variables: List[str]) -> None:
        """
        Generate a correlation heatmap for given variables.
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data not cleaned. Call clean_data() before analysis.")

        df = self.real_state_clean_data
        for var in variables:
            if var not in df.columns:
                raise ValueError(f"Variable {var} not found in the dataset.")
            if not pd.api.types.is_numeric_dtype(df[var]):
                raise ValueError(f"Variable {var} is not numeric.")

        correlation_matrix = df[variables].corr()

        fig = px.imshow(
            correlation_matrix,
            title="Correlation Heatmap",
            labels=dict(x="Variables", y="Variables", color="Correlation"),
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1
        )
        fig.update_layout(title_font=dict(size=18), title_x=0.5)

        output_folder = "src/real_estate_toolkit/analytics/outputs/"
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, "correlation_heatmap.html")
        fig.write_html(output_path)

        print(f"Correlation heatmap saved to: {output_path}")

    def create_scatter_plots(self) -> Dict[str, go.Figure]:
        """
        Create scatter plots exploring relationships between features and SalePrice.
        """
        if self.real_state_clean_data is None:
            raise ValueError("Data not cleaned. Call clean_data() before analysis.")

        output_folder = "src/real_estate_toolkit/analytics/outputs/"
        os.makedirs(output_folder, exist_ok=True)

        scatter_plots = {}

        # Scatter plot 1: House price vs. Total square footage
        fig1 = px.scatter(
            self.real_state_clean_data,
            x="TotalSF",
            y="SalePrice",
            color="OverallQual",
            title="House Price vs. Total Square Footage",
            labels={"TotalSF": "Total Square Footage", "SalePrice": "Sale Price"},
            hover_data=["YearBuilt", "Neighborhood"],
            trendline="ols"
        )
        scatter_plots["price_vs_sqft"] = fig1
        fig1.write_html(os.path.join(output_folder, "scatter_price_vs_sqft.html"))

        # Scatter plot 2: Sale price vs. Year built
        fig2 = px.scatter(
            self.real_state_clean_data,
            x="YearBuilt",
            y="SalePrice",
            color="Neighborhood",
            title="Sale Price vs. Year Built",
            labels={"YearBuilt": "Year Built", "SalePrice": "Sale Price"},
            hover_data=["OverallQual", "TotalSF"],
            trendline="ols"
        )
        scatter_plots["price_vs_year"] = fig2
        fig2.write_html(os.path.join(output_folder, "scatter_price_vs_year.html"))

        # Scatter plot 3: Overall quality vs. Sale price
        fig3 = px.scatter(
            self.real_state_clean_data,
            x="OverallQual",
            y="SalePrice",
            color="Neighborhood",
            title="Overall Quality vs. Sale Price",
            labels={"OverallQual": "Overall Quality", "SalePrice": "Sale Price"},
            hover_data=["TotalSF", "YearBuilt"],
            trendline="ols"
        )
        scatter_plots["quality_vs_price"] = fig3
        fig3.write_html(os.path.join(output_folder, "scatter_quality_vs_price.html"))

        print(f"Scatter plots saved to: {output_folder}")

        return scatter_plots
