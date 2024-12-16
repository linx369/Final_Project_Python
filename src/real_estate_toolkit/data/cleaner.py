"""Class for cleaning real estate data."""
from dataclasses import dataclass
from typing import Dict, List, Any
import re

@dataclass
class Cleaner:
    """Class for cleaning real estate data."""
    data: List[Dict[str, Any]]

    def rename_with_best_practices(self) -> None:
        """
        Rename columns with best practices (snake_case, descriptive names).
        Modifies the data in place.
        """
        if not self.data:
            return

        column_mapping = {}
        for column_name in self.data[0].keys():
            cleaned_column_name = column_name
            cleaned_column_name = re.sub(
                r'([A-Z]+)([A-Z][a-z])',
                lambda match: match.group(1).title() + match.group(2),
                cleaned_column_name
            )  # Step 2: Insert underscore between camelCase words
            cleaned_column_name = re.sub(
                r'([a-z0-9])([A-Z])',
                r'\1_\2',
                cleaned_column_name
            )  # Step 3: Handle consecutive capitals (e.g., ABCTest -> abc_test)
            cleaned_column_name = re.sub(
                r'([A-Z])([A-Z][a-z])',
                r'\1_\2',
                cleaned_column_name
            )  # Step 4: Convert to lowercase and replace remaining non-alphanumeric with underscore
            cleaned_column_name = re.sub(
                r'[^a-z0-9]+',
                '_',
                cleaned_column_name.lower()
            )  # Step 5: Clean up multiple underscores and strip leading/trailing ones
            cleaned_column_name = re.sub(r'_+', '_', cleaned_column_name).strip('_')
            column_mapping[column_name] = cleaned_column_name
        # Iterate over the rows in the data and rename the columns
        for row in self.data:
            for old_column, new_column in column_mapping.items():
                row[new_column] = row.pop(old_column)
    def na_to_none(self) -> List[Dict[str, Any]]:
        """
        Replace 'NA' strings with None in all values.
        
        Returns:
            List[Dict[str, Any]]: New list of dictionaries with NA replaced by None
        """
        cleaned_data = []
        for row in self.data:
            cleaned_row = {}
            for key, value in row.items():
                # Check for various forms of NA
                if isinstance(value, str) and value.upper() in ['NA', 'N/A', 'NULL', '']:
                    cleaned_row[key] = None
                else:
                    try:
                        cleaned_row[key] = float(value)
                    except ValueError:
                        cleaned_row[key] = value
            cleaned_data.append(cleaned_row)
        return cleaned_data