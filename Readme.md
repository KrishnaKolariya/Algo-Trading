# Algo-Trading

Algo-Trading is a Python-based project that uses Backtrader to backtest trading strategies. This repository includes scripts for:

1. **Historical Data Extraction:**  
   A script (`scripts/main.py`) fetches historical market data from an API, processes it using Pandas, and saves it as CSV files in the `h_data` directory.

2. **Backtesting:**  
   A backtesting script (`scripts/backtest.py`) implements an SMA crossover strategy integrated with target profit (0.3%) and stop-loss (0.1%) conditions. The strategy enters positions based on SMA crossover signals and exits when either the target or the stop-loss condition is met. It logs trade events and prints a detailed trade summary.

3. **Configuration Management:**  
   Sensitive credentials (API key, username, MPIN, TOTP secret) are stored in a `config.env` file, which is loaded by `scripts/config.py`. The `config.env` file is excluded from GitHub via the `.gitignore` file.

4. **Data Handling & Visualization:**  
   Historical data is processed using Pandas and visualized with Backtrader’s built-in plotting functionality (non-blocking).

5. **Trade Summary:**  
   The backtesting script outputs a trade summary (including total closed trades, long trades, short trades, winning trades, losing trades, and winning probability) in a tabular format.

---

## Setup and Installation

### 1. Clone the Repository

```bash
git clone https://github.com/KrishnaKolariya/Algo-Trading.git
cd Algo-Trading
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
```sh
cd scripts
python backtest.py
```

## File Structure
```
Algo-Trading/
├── config.env            # Contains sensitive credentials (DO NOT UPLOAD)
├── .gitignore            # Excludes config.env, virtual environments, etc.
├── requirements.txt      # List of required Python packages
├── README.md             # This documentation file
└── scripts/
    ├── main.py           # Script to fetch and save historical data
    ├── backtest.py       # Backtesting script using Backtrader
    └── config.py         # Loads environment variables from config.env

```

## Output Example
The script saves historical data in CSV format under `h_data/` as:
```
h_data/NIFTY_ONE_MINUTE_2025-01-01_2025-01-31.csv
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

