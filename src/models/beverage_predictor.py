"""
Model implementations for beverage consumption prediction.
"""
import pandas as pd
import numpy as np
from typing import Dict, Any

class BeveragePredictor:
    def __init__(self):
        # Southwest Airlines' actual beverage menu
        self.beverages = {
            'soft_drinks': [
                'Coca-Cola',
                'Diet Coke',
                'Sprite',
                'Dr Pepper',
                'Diet Dr Pepper',
                'Seagrams Ginger Ale'
            ],
            'mixers': [
                'Club Soda',
                'Tonic Water',
                'Mr & Mrs T Bloody Mary Mix',
                'Orange Juice',
                'Cranberry Apple Juice',
                'Tomato Juice'
            ],
            'hot_beverages': [
                'Community Coffee',
                'Hot Tea',
                'Hot Cocoa'
            ],
            'alcoholic': [
                'Miller Lite',
                'Dos Equis',
                'Blue Moon',
                'Lagunitas IPA',
                'Deep Eddy Vodka',
                'Jack Daniel\'s Whiskey',
                'Wild Turkey Bourbon',
                'Bacardi Rum'
            ]
        }
        
    def predict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions for Southwest's beverage menu"""
        predictions = {}
        passenger_count = df['passenger_count'].iloc[0]
        
        # Base ratios for each category
        category_ratios = {
            'soft_drinks': 0.4,    # 40% of passengers order soft drinks
            'mixers': 0.2,         # 20% order mixers/juice
            'hot_beverages': 0.25, # 25% order hot beverages
            'alcoholic': 0.15      # 15% order alcoholic beverages
        }
        
        # Generate predictions for each beverage
        for category, beverages in self.beverages.items():
            # Calculate base demand for this category
            category_demand = int(passenger_count * category_ratios[category])
            
            # Distribute among specific beverages in the category
            num_beverages = len(beverages)
            for beverage in beverages:
                # Add some randomness to make it realistic
                variation = np.random.uniform(0.7, 1.3)
                quantity = max(1, int((category_demand / num_beverages) * variation))
                predictions[beverage] = quantity
        
        return predictions 