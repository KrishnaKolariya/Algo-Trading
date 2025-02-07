# Algo Trading with SmartAPI

## Overview
The script fetches historical market data, processes it, and stores it in structured CSV files for backtesting.

## Features
- **Automated Login**: Uses API Key, MPIN, and TOTP for authentication.
- **Historical Data Extraction**: Fetches OHLCV (Open, High, Low, Close, Volume) data.
- **Data Structuring**: Splits datetime into separate Date, Time, and Timezone columns.
- **Custom File Naming**: Saves data in `h_data/` directory with filenames formatted as `Symbol_Interval_FromDate_ToDate.csv`.
- **Environment Variables Support**: Credentials are securely stored in a `.env` file.

## Installation & Setup
### 1. Clone the Repository
```sh
git clone https://github.com/yourusername/algo-trading.git
cd algo-trading
```

### 2. Create a Virtual Environment (Recommended)
```sh
python3 -m venv equity_env
source equity_env/bin/activate  # On Windows use: equity_env\Scripts\activate
```

### 3. Install Dependencies
```sh
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the **root directory** (same level as `scripts/`) and add the following:
```ini
API_KEY="your_api_key"
USERNAME="your_username"
MPIN="your_mpin"
TOTP_SECRET="your_totp_secret"
```

⚠️ **Important:** Add `.env` to `.gitignore` to prevent accidental uploads.

### 5. Run the Script
```sh
cd scripts
python main.py
```

## File Structure
```
|-- algo-trading/
    |-- h_data/                   # Stores historical data CSV files
    |-- scripts/
        |-- main.py                # Main script to fetch and save data
        |-- config.py               # Loads API credentials from .env
    |-- config.env                  # DO NOT UPLOAD (Store credentials securely)
    |-- requirements.txt            # List of required Python packages
    |-- README.md                   # Project documentation
```

## Output Example
The script saves historical data in CSV format under `h_data/` as:
```
h_data/NIFTY_ONE_MINUTE_2025-01-08_2025-01-31.csv
```
Sample CSV format:
```
Date,Time,Timezone,Open,High,Low,Close
2025-01-08,09:15,+05:30,23746.65,23751.85,23692.35,23702.75
2025-01-08,09:16,+05:30,23708.1,23708.65,23692.05,23697.2
```

## Contributing
Feel free to fork this repository and improve the script. Pull requests are welcome!

## License
This project is licensed under the MIT License.

---
**Author:** Krishna Kolariya

