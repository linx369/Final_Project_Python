from dataclasses import dataclass
from typing import Dict, List, Tuple, Any, Union
import numpy as np
import pandas as pd

@dataclass
class Descriptor:
    """Class for computing descriptive statistics on real estate data using Python and pandas."""
    data: List[Dict[str, Any]]

    def _to_dataframe(self) -> pd.DataFrame:
        """Convert the list of dicts to a pandas DataFrame."""
        return pd.DataFrame(self.data)

    def none_ratio(self, columns: List[str] = "all") -> Dict[str, float]:
        df = self._to_dataframe()
        if columns == "all":
            columns = df.columns.tolist()

        none_ratios = {}
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Invalid column name: {col}")
            col_data = df[col]
            ratio = col_data.isna().mean()
            none_ratios[col] = ratio
        return none_ratios

    def average(self, columns: List[str] = "all") -> Dict[str, float]:
        df = self._to_dataframe()
        # If columns = "all", select all numeric columns
        if columns == "all":
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        averages = {}
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Invalid column name: {col}")
            col_data = pd.to_numeric(df[col], errors='coerce')
            avg = col_data.mean(skipna=True)
            averages[col] = avg
        return averages

    def median(self, columns: List[str] = "all") -> Dict[str, float]:
        df = self._to_dataframe()
        if columns == "all":
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        medians = {}
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Invalid column name: {col}")
            col_data = pd.to_numeric(df[col], errors='coerce')
            med = col_data.median(skipna=True)
            medians[col] = med
        return medians

    def percentile(self, columns: List[str] = "all", percentile: int = 50) -> Dict[str, float]:
        df = self._to_dataframe()
        if columns == "all":
            columns = df.select_dtypes(include=[np.number]).columns.tolist()

        percentiles = {}
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Invalid column name: {col}")
            col_data = pd.to_numeric(df[col], errors='coerce').dropna()
            if col_data.empty:
                val = np.nan
            else:
                val = np.percentile(col_data, percentile)
            percentiles[col] = val
        return percentiles

    def type_and_mode(self, columns: List[str] = "all") -> Dict[str, Union[Tuple[str, float], Tuple[str, str]]]:
        df = self._to_dataframe()
        if columns == "all":
            columns = df.columns.tolist()

        type_modes = {}
        for col in columns:
            if col not in df.columns:
                raise ValueError(f"Invalid column name: {col}")

            col_data = df[col].dropna()

            # Determine type
            if pd.api.types.is_numeric_dtype(col_data):
                col_type = "numeric"
                mode_val = col_data.mode()
                mode_val = mode_val.iloc[0] if not mode_val.empty else np.nan
            else:
                col_type = "categorical"
                mode_val = col_data.mode()
                mode_val = mode_val.iloc[0] if not mode_val.empty else None

            type_modes[col] = (col_type, mode_val)
        return type_modes


@dataclass
class DescriptorNumpy:
    """Class for computing descriptive statistics on real estate data using NumPy."""
    data: np.ndarray
    column_names: List[str]

    def none_ratio(self, columns: List[str] = "all") -> Dict[str, float]:
        if columns == "all":
            columns = self.column_names
        self._validate_columns(columns)

        none_ratios = {}
        for col in columns:
            col_idx = self.column_names.index(col)
            col_data = self.data[:, col_idx]
            none_ratios[col] = np.mean(pd.isna(col_data))
        return none_ratios

    def average(self, columns: List[str] = "all") -> Dict[str, float]:
        if columns == "all":
            columns = self._numeric_columns()
        self._validate_columns(columns)

        averages = {}
        for col in columns:
            col_idx = self.column_names.index(col)
            col_data = self.data[:, col_idx].astype(float)
            averages[col] = np.nanmean(col_data)
        return averages

    def median(self, columns: List[str] = "all") -> Dict[str, float]:
        if columns == "all":
            columns = self._numeric_columns()
        self._validate_columns(columns)

        medians = {}
        for col in columns:
            col_idx = self.column_names.index(col)
            col_data = self.data[:, col_idx].astype(float)
            medians[col] = np.nanmedian(col_data)
        return medians

    def percentile(self, columns: List[str] = "all", percentile: int = 50) -> Dict[str, float]:
        if columns == "all":
            columns = self._numeric_columns()
        self._validate_columns(columns)

        percentiles = {}
        for col in columns:
            col_idx = self.column_names.index(col)
            col_data = self.data[:, col_idx].astype(float)
            percentiles[col] = np.nanpercentile(col_data, percentile)
        return percentiles

    def type_and_mode(self, columns: List[str] = "all") -> Dict[str, Union[Tuple[str, float], Tuple[str, str]]]:
        if columns == "all":
            columns = self.column_names
        self._validate_columns(columns)

        type_modes = {}
        for col in columns:
            col_idx = self.column_names.index(col)
            col_data = self.data[:, col_idx]

            col_type = "numeric" if np.issubdtype(col_data.dtype, np.number) else "categorical"

            if col_type == "numeric":
                # Compute mode for numeric columns
                # If all NaN, mode should be NaN
                clean_data = col_data[~pd.isna(col_data)]
                if len(clean_data) == 0:
                    mode = np.nan
                else:
                    vals, counts = np.unique(clean_data, return_counts=True)
                    mode = vals[np.argmax(counts)]
            else:
                # Compute mode for categorical columns
                clean_data = col_data[~pd.isna(col_data)]
                if len(clean_data) == 0:
                    mode = None
                else:
                    unique, counts = np.unique(clean_data, return_counts=True)
                    mode = unique[np.argmax(counts)]

            type_modes[col] = (col_type, mode)
        return type_modes

    def _validate_columns(self, columns: List[str]):
        invalid_columns = [col for col in columns if col not in self.column_names]
        if invalid_columns:
            raise ValueError(f"Invalid column names: {invalid_columns}")

    def _numeric_columns(self) -> List[str]:
        numeric_columns = []
        for col in self.column_names:
            col_idx = self.column_names.index(col)
            if np.issubdtype(self.data[:, col_idx].dtype, np.number):
                numeric_columns.append(col)
        return numeric_columns
