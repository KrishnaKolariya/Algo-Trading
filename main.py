# main.py

# Import necessary libraries
from SmartApi import SmartConnect  # or: from SmartApi.smartConnect import SmartConnect
import pyotp
from logzero import logger
import pandas as pd
from config import API_KEY, USERNAME, MPIN, TOTP_SECRET  # Import credentials from config.py
import os

# Initialize Smart API connection
smartApi = SmartConnect(API_KEY)

# Generate TOTP using the TOTP secret from .env
try:
    totp = pyotp.TOTP(TOTP_SECRET).now()
except Exception as e:
    logger.error("Invalid Token: The provided token is not valid.")
    raise e

# Authenticate using MPIN (as password login is no longer allowed)
data = smartApi.generateSession(USERNAME, MPIN, totp)

# Check for login errors
if data['status'] == False:
    logger.error(data)
    raise ValueError("Login failed. Check credentials or try again later.")
else:
    authToken = data['data']['jwtToken']
    refreshToken = data['data']['refreshToken']
    
    # Fetch the feed token for market data
    feedToken = smartApi.getfeedToken()
    
    # Fetch user profile
    res = smartApi.getProfile(refreshToken)
    smartApi.generateToken(refreshToken)

# Define parameters for historical data request
symbol = "NIFTY"  # Example: Change this as needed
symbol_token = "99926000"  # Replace with the correct token for your asset
exchange = "NSE"
interval = "ONE_MINUTE"
from_date = "2025-01-01"
to_date = "2025-01-31"

historicParam = {
    "exchange": exchange,
    "symboltoken": symbol_token,
    "interval": interval,
    "fromdate": f"{from_date} 09:00",  # Including time for request
    "todate": f"{to_date} 15:30"
}

# Fetch historical candle data
try:
    response = smartApi.getCandleData(historicParam)
except Exception as e:
    logger.exception(f"Historic API call failed: {e}")
    raise e

# Ensure the response contains valid data
if not response or 'data' not in response or not response['data']:
    raise ValueError("No historical data received from API.")

# Extract only the 'data' field from the response
candle_data = response['data']

# Convert the extracted data into a structured pandas DataFrame
df = pd.DataFrame(candle_data, columns=["DateTime", "Open", "High", "Low", "Close", "Volume"])

# Split "DateTime" into "Date", "Time", and "Timezone"
df[['Date', 'Time']] = df['DateTime'].str.split('T', expand=True)

# Extract timezone from the time column (if applicable)
df[['Time', 'Timezone']] = df['Time'].str.extract(r'([^+]+)(\+\d{2}:\d{2})?')

# Reorder the DataFrame with structured columns
df = df[['Date', 'Time', 'Timezone', 'Open', 'High', 'Low', 'Close']]

# Define the output directory and formatted file name
output_dir = "h_data"
os.makedirs(output_dir, exist_ok=True)  # Ensure directory exists

# Format file name as "Symbol_Interval_FromDate_ToDate.csv"
output_file = os.path.join(output_dir, f"{symbol}_{interval}_{from_date}_{to_date}.csv")

# Calculate the return as the percentage change from Open to Close.
# First, compute the return value as a float with two decimals.
return_values = ((df['Close'] - df['Open']) / df['Open'] * 100).round(2)
# Then, format these values as strings with a "%" sign appended.
df['Return'] = return_values.apply(lambda x: f"{x:.2f} %")

# Save the formatted DataFrame to a CSV file without the index column
df.to_csv(output_file, index=False)

print(f"Data has been successfully saved to {output_file}")