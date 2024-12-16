from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional
from real_estate_toolkit.agent_based_model.house import House
from real_estate_toolkit.agent_based_model.market import HousingMarket

class Segment(Enum):
    FANCY = auto()
    OPTIMIZER = auto()
    AVERAGE = auto()

@dataclass
class Consumer:
    id: int
    annual_income: float
    children_number: int
    segment: Segment
    house: Optional[House] = None
    savings: float = 0.0
    saving_rate: float = 0.3
    interest_rate: float = 0.05

    def compute_savings(self, years: int) -> None:
        """
        Calculate accumulated savings over time with annual contributions and interest.
        
        Each year:
        savings = (savings + annual_income * saving_rate) * (1 + interest_rate)

        After 5 years, starting at 20000.0, annual_income=80000.0, saving_rate=0.3,
        interest_rate=0.05, we want exactly 164771.54.
        """
        for _ in range(years):
            self.savings += self.annual_income * self.saving_rate
            self.savings *= (1 + self.interest_rate)
        # Round only after all years are computed
        self.savings = round(self.savings, 2)

    def buy_a_house(self, housing_market: HousingMarket) -> None:
        """
        Attempt to purchase a suitable house.
        
        Assume a 20% down payment is required and select a house that meets the segment criteria.
        """
        down_payment_rate = 0.2

        # Basic filtering based on segment:
        if self.segment == Segment.FANCY:
            candidate_houses = [h for h in housing_market.houses if h.available]
        elif self.segment == Segment.OPTIMIZER:
            monthly_salary = self.annual_income / 12
            candidate_houses = [h for h in housing_market.houses if h.available and h.area > 0 and (h.price / h.area) < monthly_salary]
        elif self.segment == Segment.AVERAGE:
            avg_price = housing_market.calculate_average_price()
            candidate_houses = [h for h in housing_market.houses if h.available and h.price < avg_price]
        else:
            candidate_houses = [h for h in housing_market.houses if h.available]

        # Ensure the house meets family bedroom requirements
        min_bedrooms = self.children_number + 1
        candidate_houses = [h for h in candidate_houses if h.bedrooms >= min_bedrooms]

        # Attempt to buy the first suitable house
        for house in candidate_houses:
            down_payment = house.price * down_payment_rate
            if self.savings >= down_payment:
                self.house = house
                self.savings -= down_payment
                house.sell_house()
                return

        # If no house purchased
        self.house = None
