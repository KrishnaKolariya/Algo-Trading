# config.py
import os
from dotenv import load_dotenv

# Construct the path to the config.env file in the parent directory
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.env')
load_dotenv(dotenv_path)

# Retrieve the credentials from environment variables
API_KEY = os.getenv("API_KEY")
USERNAME = os.getenv("USERNAME")
MPIN = os.getenv("MPIN")
TOTP_SECRET = os.getenv("TOTP_SECRET")

if not API_KEY or not USERNAME or not MPIN or not TOTP_SECRET:
    raise ValueError("One or more required environment variables are missing. Check your config.env file.")
