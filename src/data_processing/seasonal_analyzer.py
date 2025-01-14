import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from holidays.us import US as us_holidays

class SeasonalAnalyzer:
    """Analyzes seasonal patterns and holiday effects on beverage consumption."""
    
    # Season date ranges (month, day)
    SEASONS = {
        'winter': ((12, 21), (3, 20)),
        'spring': ((3, 21), (6, 20)),
        'summer': ((6, 21), (9, 20)),
        'fall': ((9, 21), (12, 20))
    }
    
    # Peak travel periods
    PEAK_PERIODS = {
        'spring_break': ((3, 1), (4, 15)),
        'summer_vacation': ((6, 15), (8, 31)),
        'thanksgiving': ((11, 20), (11, 30)),
        'winter_holidays': ((12, 15), (1, 5))
    }
    
    # Holiday categories
    HOLIDAY_CATEGORIES = {
        'major': [
            'New Year\'s Day',
            'Independence Day',
            'Thanksgiving',
            'Christmas Day'
        ],
        'minor': [
            'Martin Luther King Jr. Day',
            'Presidents\' Day',
            'Memorial Day',
            'Labor Day',
            'Columbus Day',
            'Veterans Day'
        ]
    }

    def __init__(self):
        self.holidays = us_holidays()
        self._init_consumption_patterns()

    def _init_consumption_patterns(self):
        """Initialize typical consumption patterns for different periods."""
        self.consumption_modifiers = {
            'seasons': {
                'winter': {
                    'hot_beverages': 1.3,
                    'soft_drinks': 0.9,
                    'water_juice': 0.8,
                    'alcoholic': 0.9
                },
                'summer': {
                    'hot_beverages': 0.7,
                    'soft_drinks': 1.4,
                    'water_juice': 1.5,
                    'alcoholic': 1.2
                }
            },
            'holidays': {
                'major': {
                    'hot_beverages': 1.1,
                    'soft_drinks': 1.2,
                    'water_juice': 1.1,
                    'alcoholic': 1.4
                },
                'minor': {
                    'hot_beverages': 1.05,
                    'soft_drinks': 1.1,
                    'water_juice': 1.05,
                    'alcoholic': 1.2
                }
            },
            'peak_travel': {
                'spring_break': {
                    'hot_beverages': 0.9,
                    'soft_drinks': 1.3,
                    'water_juice': 1.3,
                    'alcoholic': 1.5
                },
                'summer_vacation': {
                    'hot_beverages': 0.7,
                    'soft_drinks': 1.4,
                    'water_juice': 1.5,
                    'alcoholic': 1.3
                }
            }
        }

    def analyze_date(self, timestamp: int) -> Dict:
        """Analyze a specific date for seasonal and holiday factors."""
        dt = datetime.fromtimestamp(timestamp)
        
        analysis = {
            'season': self._get_season(dt),
            'is_holiday': self._is_holiday(dt),
            'holiday_category': self._get_holiday_category(dt),
            'is_peak_travel': self._is_peak_travel(dt),
            'peak_travel_period': self._get_peak_travel_period(dt),
            'day_of_week': dt.strftime('%A'),
            'is_weekend': dt.weekday() >= 5,
            'month': dt.strftime('%B'),
            'consumption_modifiers': self._get_consumption_modifiers(dt)
        }
        
        return analysis

    def _get_season(self, dt: datetime) -> str:
        """Determine the season for a given date."""
        month, day = dt.month, dt.day
        
        for season, ((start_month, start_day), (end_month, end_day)) in self.SEASONS.items():
            # Handle winter season crossing year boundary
            if season == 'winter':
                if (month, day) >= (12, 21) or (month, day) <= (3, 20):
                    return season
            else:
                if (start_month, start_day) <= (month, day) <= (end_month, end_day):
                    return season
        
        return 'winter'  # Default case

    def _is_holiday(self, dt: datetime) -> bool:
        """Check if date is a holiday."""
        return dt.date() in self.holidays

    def _get_holiday_category(self, dt: datetime) -> Optional[str]:
        """Determine holiday category if date is a holiday."""
        if not self._is_holiday(dt):
            return None
            
        holiday_name = self.holidays.get(dt.date())
        
        if holiday_name in self.HOLIDAY_CATEGORIES['major']:
            return 'major'
        elif holiday_name in self.HOLIDAY_CATEGORIES['minor']:
            return 'minor'
        
        return 'other'

    def _is_peak_travel(self, dt: datetime) -> bool:
        """Check if date falls in a peak travel period."""
        return bool(self._get_peak_travel_period(dt))

    def _get_peak_travel_period(self, dt: datetime) -> Optional[str]:
        """Determine which peak travel period the date falls in, if any."""
        month, day = dt.month, dt.day
        
        for period, ((start_month, start_day), (end_month, end_day)) in self.PEAK_PERIODS.items():
            # Handle periods crossing year boundary
            if period == 'winter_holidays':
                if (month, day) >= (12, 15) or (month, day) <= (1, 5):
                    return period
            else:
                if (start_month, start_day) <= (month, day) <= (end_month, end_day):
                    return period
        
        return None

    def _get_consumption_modifiers(self, dt: datetime) -> Dict:
        """Calculate consumption modifiers based on season, holiday, and travel period."""
        modifiers = {
            'hot_beverages': 1.0,
            'soft_drinks': 1.0,
            'water_juice': 1.0,
            'alcoholic': 1.0
        }
        
        # Apply seasonal modifiers
        season = self._get_season(dt)
        if season in ['winter', 'summer']:
            season_mods = self.consumption_modifiers['seasons'][season]
            for bev_type, mod in season_mods.items():
                modifiers[bev_type] *= mod
        
        # Apply holiday modifiers
        holiday_cat = self._get_holiday_category(dt)
        if holiday_cat in ['major', 'minor']:
            holiday_mods = self.consumption_modifiers['holidays'][holiday_cat]
            for bev_type, mod in holiday_mods.items():
                modifiers[bev_type] *= mod
        
        # Apply peak travel modifiers
        peak_period = self._get_peak_travel_period(dt)
        if peak_period in self.consumption_modifiers['peak_travel']:
            travel_mods = self.consumption_modifiers['peak_travel'][peak_period]
            for bev_type, mod in travel_mods.items():
                modifiers[bev_type] *= mod
        
        return modifiers

def main():
    """Example usage of SeasonalAnalyzer."""
    logging.basicConfig(level=logging.INFO)
    
    analyzer = SeasonalAnalyzer()
    
    # Example: Analyze current date
    now = datetime.now()
    analysis = analyzer.analyze_date(int(now.timestamp()))
    
    logging.info(f"Date analysis: {analysis}")

if __name__ == "__main__":
    main() 