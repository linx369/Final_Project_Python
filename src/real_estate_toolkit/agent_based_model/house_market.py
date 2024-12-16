from typing import List, Optional
from real_estate_toolkit.agent_based_model.house import House
import statistics
import sys
print(sys.path)


class HousingMarket:
    def __init__(self, houses: List[House]):
        self.houses: List[House] = houses

    def get_house_by_id(self, house_id: int) -> Optional[House]:
        """
        Retrieve specific house by ID.
        """
        for house in self.houses:
            if house.id == house_id:
                return house
        return None

    def calculate_average_price(self, bedrooms: Optional[int] = None) -> float:
        """
        Calculate average house price, optionally filtered by bedrooms.
        """
        filtered_houses = self.houses if bedrooms is None else [house for house in self.houses if house.bedrooms == bedrooms]

        if not filtered_houses:
            return 0.0

        prices = [house.price for house in filtered_houses]
        return statistics.mean(prices)

    def get_houses_that_meet_requirements(self, max_price: int, segment) -> Optional[List[House]]:
        """
        Filter houses based on buyer requirements.

        'segment' is expected to be an enum member, e.g. Segment.AVERAGE.
        We will convert it to a string using segment.name.
        """
        filtered_houses = [
            house for house in self.houses
            if house.price <= max_price
            and house.segment is not None
            and house.segment.lower() == segment.name.lower()
        ]

        return filtered_houses if filtered_houses else None
