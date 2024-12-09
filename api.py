from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import logging
from typing import Optional
import storage

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load the last used symbol from storage
current_symbol = storage.get_last_symbol()

class SymbolUpdate(BaseModel):
    symbol: str

@app.get("/current")
async def get_current_symbol():
    """Get the currently displayed symbol"""
    return {"symbol": current_symbol}

@app.post("/update")
async def update_symbol(update: SymbolUpdate):
    """Update the symbol to display"""
    global current_symbol
    try:
        current_symbol = update.symbol
        # Save the new symbol to storage
        storage.save_last_symbol(current_symbol)
        logger.info(f"Updated symbol to: {current_symbol}")
        return {"status": "success", "symbol": current_symbol}
    except Exception as e:
        logger.error(f"Error updating symbol: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
