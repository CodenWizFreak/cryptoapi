# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import json
from pathlib import Path
import os

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Data model for wallet address
class WalletAddress(BaseModel):
    address: str

class RedirectResponse(BaseModel):
    url: str

# File to store the wallet address
WALLET_FILE = "wallet_address.json"

def save_wallet_address(address: str):
    """Save wallet address to a file that Streamlit can read"""
    data = {"wallet_address": address, "connected": True}
    with open(WALLET_FILE, "w") as f:
        json.dump(data, f)

def get_wallet_address():
    """Read wallet address from file"""
    if not Path(WALLET_FILE).exists():
        return {"wallet_address": "", "connected": False}
    with open(WALLET_FILE, "r") as f:
        return json.load(f)
    
@app.get("/api/")
async def read_root():
    return {"message": "Welcome to Cryptonian API!"}  

@app.post("/api/connect-wallet")
async def connect_wallet(wallet: WalletAddress):
    try:
        save_wallet_address(wallet.address)
        return {"status": "success", "message": "Wallet connected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/wallet-status")
async def wallet_status():
    return get_wallet_address()

@app.post("/api/disconnect-wallet")
async def disconnect_wallet():
    try:
        if Path(WALLET_FILE).exists():
            os.remove(WALLET_FILE)
        return {"status": "success", "message": "Wallet disconnected successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/redirect-to-next")
async def redirect_to_next(request: RedirectResponse):
    """Endpoint to handle redirection to Next.js app"""
    try:
        # First disconnect the wallet
        if Path(WALLET_FILE).exists():
            os.remove(WALLET_FILE)
        # Return a redirect response
        return RedirectResponse(url=request.url, status_code=303)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
