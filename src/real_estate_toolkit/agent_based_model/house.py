from enum import Enum
from dataclasses import dataclass
from typing import Optional

class QualityScore(Enum):
    EXCELLENT = 5
    GOOD = 4
    AVERAGE = 3
    FAIR = 2
    POOR = 1

@dataclass
class House:
    id: int
    price: float
    area: float
    bedrooms: int
    year_built: int
    quality_score: Optional[QualityScore]
    available: bool = True
    segment: Optional[str] = None
 # Add this line to define the segment attribute

    def calculate_price_per_square_foot(self) -> float:
        """
        Calculate and return the price per square foot.
        """
        if self.area == 0:
            return 0.0  # Handle edge case where area is zero
        price_per_sqft = self.price / self.area
        return round(price_per_sqft, 2)

    def is_new_construction(self, current_year: int = 2024) -> bool:
        """
        Determine if house is considered new construction (< 5 years old).
        """
        age = current_year - self.year_built
        if age < 0:
            return False  # Invalid year_built in the future
        return age < 5

    def get_quality_score(self) -> None:
        """
        Generate a quality score based on house attributes.
        """
        if self.quality_score is not None:
            return  # Quality score already set

        current_year = 2024
        age = current_year - self.year_built

        # Age score
        if age <= 5:
            age_score = 5
        elif age <= 10:
            age_score = 4
        elif age <= 20:
            age_score = 3
        elif age <= 50:
            age_score = 2
        else:
            age_score = 1

        # Size score
        if self.area >= 3000:
            size_score = 5
        elif self.area >= 2000:
            size_score = 4
        elif self.area >= 1500:
            size_score = 3
        elif self.area >= 1000:
            size_score = 2
        else:
            size_score = 1

        # Bedrooms score
        if self.bedrooms >= 5:
            bedrooms_score = 5
        elif self.bedrooms >= 4:
            bedrooms_score = 4
        elif self.bedrooms >= 3:
            bedrooms_score = 3
        elif self.bedrooms >= 2:
            bedrooms_score = 2
        else:
            bedrooms_score = 1

        # Calculate average score
        average_score = (age_score + size_score + bedrooms_score) / 3

        # Map to QualityScore
        if average_score >= 4.5:
            self.quality_score = QualityScore.EXCELLENT
        elif average_score >= 3.5:
            self.quality_score = QualityScore.GOOD
        elif average_score >= 2.5:
            self.quality_score = QualityScore.AVERAGE
        elif average_score >= 1.5:
            self.quality_score = QualityScore.FAIR
        else:
            self.quality_score = QualityScore.POOR

    def sell_house(self) -> None:
        """
        Mark house as sold.
        """
        self.available = False
