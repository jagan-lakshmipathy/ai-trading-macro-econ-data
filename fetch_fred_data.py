"""
FRED Economic Data Fetcher

This script fetches economic data from the Federal Reserve Economic Data (FRED) API.
It supports configurable time periods and ticker symbols.

Usage:
    python fetch_fred_data.py --period 5y
    python fetch_fred_data.py --period 3y --output data.csv
    python fetch_fred_data.py --config custom_config.json
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from fredapi import Fred
from dotenv import load_dotenv


class FREDDataFetcher:
    """Fetch economic data from FRED API with configurable parameters."""
    
    def __init__(self, api_key: str = None):
        """
        Initialize FRED API client.
        
        Args:
            api_key: FRED API key. If None, will look for FRED_API_KEY environment variable.
        """
        if api_key is None:
            api_key = os.getenv('FRED_API_KEY')
            if not api_key:
                raise ValueError(
                    "FRED API key not provided. Set FRED_API_KEY environment variable "
                    "or pass api_key parameter."
                )
        self.fred = Fred(api_key=api_key)
    
    def parse_period(self, period_str: str) -> datetime:
        """
        Parse period string to get start date.
        
        Args:
            period_str: Period string (e.g., '5y', '3y', '1y', '6m', '3m')
        
        Returns:
            Start date as datetime object
        """
        period_map = {
            'y': 'years',
            'm': 'months',
            'd': 'days',
        }
        
        # Extract number and unit
        if len(period_str) < 2:
            raise ValueError(f"Invalid period format: {period_str}")
        
        number = int(period_str[:-1])
        unit = period_str[-1].lower()
        
        if unit not in period_map:
            raise ValueError(
                f"Invalid period unit: {unit}. Use 'y' (years), 'm' (months), or 'd' (days)."
            )
        
        # Calculate start date
        end_date = datetime.now()
        if unit == 'y':
            start_date = end_date - timedelta(days=number * 365)
        elif unit == 'm':
            start_date = end_date - timedelta(days=number * 30)
        else:  # days
            start_date = end_date - timedelta(days=number)
        
        return start_date
    
    def fetch_series(self, series_id: str, start_date: datetime) -> pd.Series:
        """
        Fetch a single data series from FRED.
        
        Args:
            series_id: FRED series ID (e.g., 'FEDFUNDS')
            start_date: Start date for data retrieval
        
        Returns:
            Pandas Series with the data
        """
        try:
            data = self.fred.get_series(series_id, observation_start=start_date)
            print(f"✓ Successfully fetched {series_id}: {len(data)} observations")
            return data
        except Exception as e:
            print(f"✗ Error fetching {series_id}: {str(e)}")
            return pd.Series()
    
    def fetch_multiple_series(
        self, 
        series_ids: List[str], 
        period: str = '5y'
    ) -> pd.DataFrame:
        """
        Fetch multiple data series from FRED.
        
        Args:
            series_ids: List of FRED series IDs
            period: Time period string (e.g., '5y', '3y', '1y')
        
        Returns:
            DataFrame with all series
        """
        start_date = self.parse_period(period)
        print(f"\nFetching data from {start_date.strftime('%Y-%m-%d')} to present")
        print(f"Period: {period}")
        print("-" * 60)
        
        data_dict = {}
        for series_id in series_ids:
            series_data = self.fetch_series(series_id, start_date)
            if not series_data.empty:
                data_dict[series_id] = series_data
        
        # Combine all series into a DataFrame
        if data_dict:
            df = pd.DataFrame(data_dict)
            print("-" * 60)
            print(f"\nTotal series fetched: {len(df.columns)}")
            print(f"Date range: {df.index.min()} to {df.index.max()}")
            print(f"Total rows: {len(df)}")
            return df
        else:
            print("No data was fetched.")
            return pd.DataFrame()
    
    def save_data(self, df: pd.DataFrame, output_file: str):
        """
        Save DataFrame to CSV file.
        
        Args:
            df: DataFrame to save
            output_file: Output file path
        """
        if df.empty:
            print("No data to save.")
            return
        
        df.to_csv(output_file)
        print(f"\nData saved to: {output_file}")
        print(f"File size: {os.path.getsize(output_file) / 1024:.2f} KB")


def load_config(config_file: str) -> Dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_file: Path to configuration file
    
    Returns:
        Configuration dictionary
    """
    with open(config_file, 'r') as f:
        return json.load(f)


def main():
    """Main entry point for the script."""
    # Load environment variables from .env file
    load_dotenv()
    
    # Get default values from environment variables
    default_period = os.getenv('DEFAULT_PERIOD', '5y')
    default_config = os.getenv('DEFAULT_CONFIG_FILE', 'config.json')
    default_output = os.getenv('DEFAULT_OUTPUT_FILE', 'fred_data.csv')
    
    parser = argparse.ArgumentParser(
        description='Fetch economic data from FRED API',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch data for the last 5 years
  python fetch_fred_data.py --period 5y
  
  # Fetch data for the last 3 years with custom output
  python fetch_fred_data.py --period 3y --output my_data.csv
  
  # Use custom configuration file
  python fetch_fred_data.py --config custom_config.json
  
  # Fetch data for last 6 months
  python fetch_fred_data.py --period 6m
        """
    )
    
    parser.add_argument(
        '--period',
        type=str,
        default=default_period,
        help=f'Time period (e.g., 5y, 3y, 1y, 6m, 3m, 90d). Default: {default_period}'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default=default_config,
        help=f'Path to configuration file. Default: {default_config}'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=default_output,
        help=f'Output CSV file path. Default: {default_output}'
    )
    
    parser.add_argument(
        '--api-key',
        type=str,
        help='FRED API key (overrides FRED_API_KEY environment variable)'
    )
    
    args = parser.parse_args()
    
    try:
        # Load configuration
        config = load_config(args.config)
        series_ids = config.get('series_ids', [])
        
        if not series_ids:
            print("Error: No series IDs found in configuration file.")
            return
        
        # Initialize fetcher
        fetcher = FREDDataFetcher(api_key=args.api_key)
        
        # Fetch data
        df = fetcher.fetch_multiple_series(series_ids, args.period)
        
        # Save data
        if not df.empty:
            fetcher.save_data(df, args.output)
            
            # Display summary statistics
            print("\n" + "=" * 60)
            print("DATA SUMMARY")
            print("=" * 60)
            print(df.describe())
            
    except FileNotFoundError:
        print(f"Error: Configuration file '{args.config}' not found.")
        print("Please create a config.json file or specify a different config file.")
    except ValueError as e:
        print(f"Error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()
