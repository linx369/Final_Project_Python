"""Module for loading and basic processing of real estate data."""
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Any
import csv

@dataclass
class DataLoader:
    """Class for loading and basic processing of real estate data."""
    data_path: Path = Path("/Users/tomowen/Desktop/real_estate_toolkit/files/train.csv")

    def load_data_from_csv(self) -> List[Dict[str, Any]]:
        """
        Load data from CSV file into a list of dictionaries.
        
        Returns:
            List[Dict[str, Any]]: List where each item is a dictionary representing a row
        
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            csv.Error: If the CSV file is empty or malformed
        """
        if not self.data_path.exists():
            raise FileNotFoundError(f"File not found: {self.data_path}")
        try:
            data: List[Dict[str, Any]] = []
            with open(self.data_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                for row in csv_reader:
                    data.append(dict(row))
            if not data:
                raise ValueError("CSV file is empty")
            return data
        except csv.Error as e:
            raise csv.Error(f"Error reading CSV file: {e}")

    def validate_columns(self, required_columns: List[str]) -> bool:
        """
        Validate that all required columns are present in the dataset.
        
        Args:
            required_columns: List of column names that must be present
        
        Returns:
            bool: True if all required columns are present, False otherwise
        
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            csv.Error: If the CSV file is empty or malformed
        """
        try:
            # Load just the header row to check columns
            with open(self.data_path, 'r', encoding='utf-8') as csv_file:
                csv_reader = csv.reader(csv_file)
                csv_header = next(csv_reader)
            # Check if all required columns are in header
            return all(col in csv_header for col in required_columns)
        except (FileNotFoundError, csv.Error):
            return False