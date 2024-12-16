from enum import Enum, auto
from dataclasses import dataclass
from random import gauss, randint, choice
from typing import List, Dict, Any
from real_estate_toolkit.agent_based_model.house import House
from real_estate_toolkit.agent_based_model.house_market import HousingMarket
from real_estate_toolkit.agent_based_model.consumers import Segment, Consumer


class CleaningMarketMechanism(Enum):
    INCOME_ORDER_DESCENDANT = auto()
    INCOME_ORDER_ASCENDANT = auto()
    RANDOM = auto()


@dataclass
class AnnualIncomeStatistics:
    minimum: float
    average: float
    standard_deviation: float
    maximum: float


@dataclass
class ChildrenRange:
    minimum: float = 0
    maximum: float = 5


@dataclass
class Simulation:
    housing_market_data: List[Dict[str, Any]]
    consumers_number: int
    years: int
    annual_income: AnnualIncomeStatistics
    children_range: ChildrenRange
    cleaning_market_mechanism: CleaningMarketMechanism
    down_payment_percentage: float = 0.2
    saving_rate: float = 0.3
    interest_rate: float = 0.05

    def create_housing_market(self) -> None:
        """
        Initialize market with houses.
        
        Extract only the fields required by House:
        House fields: id, price, area, bedrooms, year_built, quality_score, available, segment
        Map CSV columns to these fields:
        - id: "Id"
        - price: "SalePrice"
        - area: "GrLivArea"
        - bedrooms: "BedroomAbvGr"
        - year_built: "YearBuilt"
        Set quality_score = None, available = True, segment = "AVERAGE"
        Ignore all other fields.
        """
        houses = []
        for original_data in self.housing_market_data:
            # Extract and rename the necessary fields:
            hd = {}
            hd["id"] = int(original_data["Id"])
            hd["price"] = float(original_data["SalePrice"])
            hd["area"] = float(original_data["GrLivArea"])
            hd["bedrooms"] = int(original_data["BedroomAbvGr"])
            hd["year_built"] = int(original_data["YearBuilt"])
            # Set defaults
            hd["quality_score"] = None
            hd["available"] = True
            hd["segment"] = "AVERAGE"

            # Now create the House object with a clean dictionary
            houses.append(House(**hd))

        self.housing_market = HousingMarket(houses)

    def create_consumers(self) -> None:
        """
        Generate a consumer population.
        """
        consumers = []
        for _ in range(self.consumers_number):
            # Generate annual income within the specified range
            while True:
                income = gauss(self.annual_income.average, self.annual_income.standard_deviation)
                if self.annual_income.minimum <= income <= self.annual_income.maximum:
                    break

            # Generate number of children
            children_number = randint(self.children_range.minimum, self.children_range.maximum)

            # Assign a random segment
            segment = choice(list(Segment))

            # Create a Consumer and add it to the list
            consumers.append(Consumer(
                id=len(consumers) + 1,
                annual_income=income,
                children_number=children_number,
                segment=segment,
                house=None,
                savings=0.0,
                saving_rate=self.saving_rate,
                interest_rate=self.interest_rate
            ))

        self.consumers = consumers

    def compute_consumers_savings(self) -> None:
        """
        Calculate savings for all consumers.
        """
        for consumer in self.consumers:
            consumer.compute_savings(self.years)

    def clean_the_market(self) -> None:
        """
        Execute market transactions.
        """
        if self.cleaning_market_mechanism == CleaningMarketMechanism.INCOME_ORDER_DESCENDANT:
            self.consumers.sort(key=lambda x: x.annual_income, reverse=True)
        elif self.cleaning_market_mechanism == CleaningMarketMechanism.INCOME_ORDER_ASCENDANT:
            self.consumers.sort(key=lambda x: x.annual_income)
        elif self.cleaning_market_mechanism == CleaningMarketMechanism.RANDOM:
            from random import shuffle
            shuffle(self.consumers)

        # Consumers attempt to buy houses
        for consumer in self.consumers:
            consumer.buy_a_house(self.housing_market)

    def compute_owners_population_rate(self) -> float:
        """
        Compute the owners population rate.
        """
        owners = sum(1 for consumer in self.consumers if consumer.house is not None)
        return owners / len(self.consumers)

    def compute_houses_availability_rate(self) -> float:
        """
        Compute the houses availability rate.
        Houses are available if their 'available' attribute is True.
        """
        available_houses = sum(1 for house in self.housing_market.houses if house.available)
        return available_houses / len(self.housing_market.houses)
