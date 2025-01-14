import pandas as pd
import numpy as np
from src.models.beverage_predictor import BeveragePredictor
from datetime import datetime, timedelta

class EconomicImpactAnalyzer:
    def __init__(self):
        # Average weights per beverage type (in lbs)
        self.beverage_weights = {
            'soft_drinks': 0.375,  # 12oz can
            'hot_beverages': 0.1,  # Per serving with supplies
            'water': 1.1,         # 16.9oz bottle
            'juice': 0.5,         # 8oz bottle
            'beer': 0.375,        # 12oz can
            'wine': 0.5,          # 187ml bottle
            'spirits': 0.2        # Mini bottle
        }
        
        # Cost factors
        self.fuel_cost_per_lb_per_hour = 0.05  # Estimated fuel cost per pound per flight hour
        self.beverage_costs = {
            'soft_drinks': 0.50,
            'hot_beverages': 0.30,
            'water': 0.75,
            'juice': 1.00,
            'beer': 2.50,
            'wine': 4.00,
            'spirits': 5.00
        }
        
    def analyze_weight_savings(self, baseline_stock, optimized_stock, flight_hours):
        """Calculate weight and fuel savings"""
        baseline_weight = sum(baseline_stock[bev] * self.beverage_weights[bev] 
                            for bev in baseline_stock)
        optimized_weight = sum(optimized_stock[bev] * self.beverage_weights[bev] 
                             for bev in optimized_stock)
        
        weight_reduction = baseline_weight - optimized_weight
        fuel_savings = weight_reduction * self.fuel_cost_per_lb_per_hour * flight_hours
        
        return {
            'weight_reduction_lbs': weight_reduction,
            'fuel_savings_usd': fuel_savings
        }
        
    def analyze_inventory_cost_savings(self, baseline_stock, optimized_stock):
        """Calculate inventory cost savings"""
        baseline_cost = sum(baseline_stock[bev] * self.beverage_costs[bev] 
                          for bev in baseline_stock)
        optimized_cost = sum(optimized_stock[bev] * self.beverage_costs[bev] 
                           for bev in optimized_stock)
        
        return {
            'inventory_cost_reduction': baseline_cost - optimized_cost
        }
        
    def analyze_environmental_impact(self, weight_reduction, flight_hours):
        """Calculate CO2 reduction from weight savings"""
        # Average CO2 emissions per pound of fuel: 3.15 lbs CO2 per lb fuel
        # Assuming 1 lb weight reduction saves 0.03 lb fuel per hour
        fuel_reduction = weight_reduction * 0.03 * flight_hours
        co2_reduction = fuel_reduction * 3.15
        
        return {
            'co2_reduction_lbs': co2_reduction
        }
        
def main():
    analyzer = EconomicImpactAnalyzer()
    predictor = BeveragePredictor()
    predictor.load_model('models/beverage_predictor.joblib')
    
    # Generate sample flight data
    test_flights = pd.DataFrame({
        'flight_number': ['SWA1234', 'SWA5678', 'SWA9012'],
        'timestamp': [int(datetime.now().timestamp())] * 3,
        'duration_hours': [2.5, 3.75, 1.5],
        'passenger_count': [143, 175, 143],
        'is_business_route': [1, 0, 0],
        'is_vacation_route': [0, 1, 0],
        'is_holiday': [0, 0, 1]
    })
    
    # Get model predictions
    predictions = predictor.predict(test_flights)
    
    # Analyze impact for each flight
    total_savings = {
        'weight_reduction_lbs': 0,
        'fuel_savings_usd': 0,
        'inventory_cost_reduction': 0,
        'co2_reduction_lbs': 0
    }
    
    for i, flight in test_flights.iterrows():
        # Simulate baseline stock (typical 25% buffer)
        baseline_stock = {k: v * 1.25 for k, v in predictions[i].items()}
        optimized_stock = predictions[i]
        
        # Calculate savings
        weight_savings = analyzer.analyze_weight_savings(
            baseline_stock, optimized_stock, flight['duration_hours'])
        inventory_savings = analyzer.analyze_inventory_cost_savings(
            baseline_stock, optimized_stock)
        environmental_impact = analyzer.analyze_environmental_impact(
            weight_savings['weight_reduction_lbs'], flight['duration_hours'])
        
        # Accumulate savings
        total_savings['weight_reduction_lbs'] += weight_savings['weight_reduction_lbs']
        total_savings['fuel_savings_usd'] += weight_savings['fuel_savings_usd']
        total_savings['inventory_cost_reduction'] += inventory_savings['inventory_cost_reduction']
        total_savings['co2_reduction_lbs'] += environmental_impact['co2_reduction_lbs']
    
    # Print results
    print("\nEconomic Impact Analysis")
    print("=======================")
    print(f"Total Weight Reduction: {total_savings['weight_reduction_lbs']:.2f} lbs")
    print(f"Fuel Cost Savings: ${total_savings['fuel_savings_usd']:.2f}")
    print(f"Inventory Cost Savings: ${total_savings['inventory_cost_reduction']:.2f}")
    print(f"CO2 Emissions Reduction: {total_savings['co2_reduction_lbs']:.2f} lbs")
    
    # Annualized projections (assuming similar savings across 1000 daily flights)
    annual_multiplier = 365 * 1000 / len(test_flights)
    print("\nAnnualized Projections (1000 daily flights)")
    print("==========================================")
    print(f"Annual Weight Reduction: {total_savings['weight_reduction_lbs'] * annual_multiplier:.2f} lbs")
    print(f"Annual Fuel Cost Savings: ${total_savings['fuel_savings_usd'] * annual_multiplier:.2f}")
    print(f"Annual Inventory Cost Savings: ${total_savings['inventory_cost_reduction'] * annual_multiplier:.2f}")
    print(f"Annual CO2 Emissions Reduction: {total_savings['co2_reduction_lbs'] * annual_multiplier:.2f} lbs")

if __name__ == '__main__':
    main() 