import json
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

STORAGE_FILE = "storage.json"
DEFAULT_DATA = {
    "last_symbol": "AAPL"  # Default symbol if no storage exists
}

def load_data() -> dict:
    """Load data from storage file"""
    try:
        if os.path.exists(STORAGE_FILE):
            with open(STORAGE_FILE, 'r') as f:
                return json.load(f)
        return DEFAULT_DATA.copy()
    except Exception as e:
        logger.error(f"Error loading storage: {str(e)}")
        return DEFAULT_DATA.copy()

def save_data(data: dict):
    """Save data to storage file"""
    try:
        with open(STORAGE_FILE, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving to storage: {str(e)}")

def get_last_symbol() -> str:
    """Get the last used symbol"""
    return load_data().get("last_symbol", DEFAULT_DATA["last_symbol"])

def save_last_symbol(symbol: str):
    """Save the last used symbol"""
    data = load_data()
    data["last_symbol"] = symbol
    save_data(data)
    logger.info(f"Saved last symbol: {symbol}")
