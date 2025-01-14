import requests
import json
from datetime import datetime
import pandas as pd
from tabulate import tabulate

def format_predictions(response_json):
    """Format the predictions into readable tables by category."""
    predictions = response_json['predictions']
    
    for flight in predictions:
        flight_num = flight['flight_number']
        pred = flight['predictions']
        
        print(f"\n=== Flight {flight_num} Predictions ===\n")
        
        # Format each beverage category
        for category, beverages in pred.items():
            # Create a DataFrame for this category
            rows = []
            for beverage, amount in beverages.items():
                rows.append({
                    'Beverage': beverage.replace('_', ' ').title(),
                    'Servings': amount
                })
            
            df = pd.DataFrame(rows)
            df = df.sort_values('Servings', ascending=False)
            
            print(f"\n{category.replace('_', ' ').title()}:")
            print(tabulate(df, headers='keys', tablefmt='pretty', showindex=False))
        
        # Print category totals
        print("\nCategory Totals:")
        totals = pd.DataFrame([
            {'Category': cat.replace('_', ' ').title(), 
             'Total Servings': sum(beverages.values())}
            for cat, beverages in pred.items()
        ])
        print(tabulate(totals, headers='keys', tablefmt='pretty', showindex=False))
        print("\n" + "="*50)

def main():
    # Make the prediction request
    url = 'http://localhost:8000/predict'
    files = {'file': open('sample_prediction_data.csv', 'rb')}
    
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        
        # Format and display predictions
        format_predictions(response.json())
        
    except requests.exceptions.RequestException as e:
        print(f"Error making prediction request: {str(e)}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 