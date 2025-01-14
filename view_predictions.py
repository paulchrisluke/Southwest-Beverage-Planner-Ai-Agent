import requests
import json
from tabulate import tabulate
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def format_predictions(response_data):
    """Format predictions into tables by category"""
    for flight_data in response_data:
        flight_number = flight_data['flight_number']
        predictions = flight_data['predictions']
        
        print(f"\nPredictions for Flight {flight_number}:")
        print("=" * 50)
        
        for category, beverages in predictions.items():
            # Create a DataFrame for this category
            df = pd.DataFrame(list(beverages.items()), columns=['Beverage', 'Predicted Amount'])
            df = df.sort_values('Predicted Amount', ascending=False)
            
            print(f"\n{category.upper()}:")
            print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))
            print(f"Total {category}: {df['Predicted Amount'].sum()}")

def main():
    try:
        # Make prediction request
        with open('sample_data.csv', 'rb') as f:
            files = {'file': ('sample_data.csv', f, 'text/csv')}
            response = requests.post('http://localhost:8000/predict', files=files)
            
            if response.status_code == 200:
                predictions = response.json()
                format_predictions(predictions)
            else:
                logger.error(f"Error: {response.status_code} - {response.text}")
                
    except requests.exceptions.RequestException as e:
        logger.error(f"Error making prediction request: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")

if __name__ == '__main__':
    main() 