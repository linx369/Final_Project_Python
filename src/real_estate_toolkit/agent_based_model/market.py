from typing import List, Optional
from real_estate_toolkit.agent_based_model.house import House
import statistics


class HousingMarket:
    def __init__(self, houses: List[House]):
        self.houses: List[House] = houses
   
    def get_house_by_id(self, house_id: int) -> Optional[House]:
        """
        Retrieve specific house by ID.
       
        Implementation tips:
        - Use efficient search method
        - Handle non-existent IDs
        """
        # Efficient search using list comprehension
        for house in self.houses:
            if house.id == house_id:
                return house
        # Return None if the house ID is not found
        return None


    def calculate_average_price(self, bedrooms: Optional[int] = None) -> float:
        """
        Calculate average house price, optionally filtered by bedrooms.
       
        Implementation tips:
        - Handle empty lists
        - Consider using statistics module
        - Implement bedroom filtering efficiently
        """
        # Filter houses based on the number of bedrooms if specified
        filtered_houses = self.houses if bedrooms is None else [house for house in self.houses if house.bedrooms == bedrooms]
       
        # Handle empty list case
        if not filtered_houses:
            return 0.0
       
        # Calculate average price using the statistics module
        prices = [house.price for house in filtered_houses]
        return statistics.mean(prices)


    def get_houses_that_meet_requirements(self, max_price: int, segment: str) -> Optional[List[House]]:
        """
        Filter houses based on buyer requirements.
       
        Implementation tips:
        - Consider multiple filtering criteria
        - Implement efficient filtering
        - Handle case when no houses match
        """
        # Filter houses based on max_price and segment criteria
        filtered_houses = [
            house for house in self.houses
            if house.price <= max_price and house.segment.lower() == segment.lower()
        ]
       
        # Return None if no houses match the criteria
        return filtered_houses if filtered_houses else None