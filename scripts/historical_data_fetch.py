import time
import pandas as pd
import os
from SmartApi import SmartConnect
import pyotp
from logzero import logger
from config import API_KEY, USERNAME, MPIN, TOTP_SECRET
from datetime import datetime, timedelta

# Initialize API Connection
smartApi = SmartConnect(API_KEY)

# Generate TOTP
try:
    totp = pyotp.TOTP(TOTP_SECRET).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

# Authenticate
data = smartApi.generateSession(USERNAME, MPIN, totp)
if not data.get('status'):
    logger.error(data)
    raise ValueError("Login failed. Check credentials or try again later.")

authToken = data['data']['jwtToken']
refreshToken = data['data']['refreshToken']
feedToken = smartApi.getfeedToken()
smartApi.generateToken(refreshToken)

# Set parameters
symbol = "NIFTY"
symbol_token = "99926000"
exchange = "NSE"
interval = "ONE_MINUTE"
start_year = 2005
end_year = 2025
output_dir = "h_data"
os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists

# Generate all date ranges (30-day intervals)
current_date = datetime(start_year, 1, 1)
end_date = datetime(end_year, 1, 1)

all_data = []
missing_dates = []
first_date, last_date = None, None  # To store first and last dates for naming

# Function to fetch data with rate limiting and retries
def fetch_historical_data(from_date, to_date):
    historicParam = {
        "exchange": exchange,
        "symboltoken": symbol_token,
        "interval": interval,
        "fromdate": f"{from_date} 09:00",
        "todate": f"{to_date} 15:30"
    }

    for attempt in range(3):  # Retry up to 3 times if request fails
        try:
            response = smartApi.getCandleData(historicParam)
            if response and "data" in response and response["data"]:
                return response["data"]
            else:
                logger.warning(f"No data received for {from_date} to {to_date}, retrying...")
        except Exception as e:
            logger.error(f"Error fetching data for {from_date} to {to_date}: {e}")
        time.sleep(5)  # Wait before retrying

    logger.error(f"Failed to fetch data for {from_date} to {to_date} after 3 attempts.")
    return None  # Return None if all retries fail

while current_date < end_date:
    next_date = current_date + timedelta(days=30)
    from_date = current_date.strftime("%Y-%m-%d")
    to_date = next_date.strftime("%Y-%m-%d")

    print(f"Fetching data from {from_date} to {to_date}...")
    data = fetch_historical_data(from_date, to_date)

    if data:
        if first_date is None:
            first_date = from_date  # Capture first date for filename
        last_date = to_date  # Capture last date for filename

        df = pd.DataFrame(data, columns=["DateTime", "Open", "High", "Low", "Close", "Volume"])
        df[['Date', 'Time']] = df['DateTime'].str.split('T', expand=True)
        df[['Time', 'Timezone']] = df['Time'].str.extract(r'([^+]+)(\+\d{2}:\d{2})?')
        df = df[['Date', 'Time', 'Timezone', 'Open', 'High', 'Low', 'Close']]
        all_data.append(df)
    else:
        missing_dates.append((from_date, to_date))  # Log missing data

    time.sleep(0.4)  # **Rate limiting: Max 3 requests per second**
    current_date = next_date  # Move to next date range

# Save all data to HDF file
if all_data and first_date and last_date:
    hdf_file = os.path.join(output_dir, f"{symbol}_{interval}_{first_date}_{last_date}.h5")
    final_df = pd.concat(all_data, ignore_index=True)
    final_df.to_hdf(hdf_file, key="data", mode="w")
    print(f"Data successfully saved to {hdf_file}")

# Save missing data log **inside h_data directory**
if missing_dates:
    missing_data_file = os.path.join(output_dir, "missing_data.log")
    with open(missing_data_file, "w") as f:
        for start, end in missing_dates:
            f.write(f"Missing data: {start} to {end}\n")

    print(f"Missing date ranges have been logged in {missing_data_file}")
