# Quick Start Guide

## 1. Install Dependencies

```bash
pip install -r requirements.txt
```

## 2. Get Your FRED API Key

1. Go to https://fred.stlouisfed.org/
2. Create a free account
3. Get your API key from https://fred.stlouisfed.org/docs/api/api_key.html

## 3. Set Up Your .env File

```bash
# Copy the example file
cp .env.example .env

# Edit the .env file with your favorite editor
nano .env
```

Add your FRED API key to the `.env` file:
```env
FRED_API_KEY=your_actual_api_key_here
DEFAULT_PERIOD=5y
DEFAULT_OUTPUT_FILE=fred_data.csv
DEFAULT_CONFIG_FILE=config.json
```

## 4. Run the Script

```bash
# Fetch 5 years of data (default)
python fetch_fred_data.py

# Fetch 3 years of data
python fetch_fred_data.py --period 3y

# Fetch 1 year of data
python fetch_fred_data.py --period 1y
```

## 5. Check Your Data

Open `fred_data.csv` to see your fetched economic data!

## Customizing Series

Edit `config.json` to add or remove economic indicators:

```json
{
  "series_ids": [
    "FEDFUNDS",
    "CPIAUCSL",
    "GDPC1"
  ]
}
```

## Examples

### Inflation Data Only
```bash
python fetch_fred_data.py --config example_inflation_config.json --period 3y
```

### Recent Labor Market Data
```bash
python fetch_fred_data.py --period 6m --output labor_market.csv
```

Edit the config.json to include only: UNRATE, PAYEMS

## Need Help?

See the full [README.md](README.md) for detailed documentation.
