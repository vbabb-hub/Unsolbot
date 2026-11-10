import requests
import pandas as pd

def get_sol_price():
    """Recupera il prezzo corrente di SOL da CoinCap"""
    url = "https://api.coincap.io/v2/assets/solana"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data['data']['priceUsd'])
    except Exception as e:
        print(f"Errore nel recupero del prezzo: {e}")
        return None

def analyze_market():
    """Recupera lo storico recente e calcola la SMA"""
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        prices = [item[1] for item in data['prices']]
        
        df = pd.DataFrame(prices, columns=['close'])
        df['sma_10'] = df['close'].rolling(window=10).mean()
        
        current_price = df['close'].iloc[-1]
        current_sma = df['sma_10'].iloc[-1]
        
        if pd.isna(current_sma):
            current_sma = current_price
            
        if current_price > current_sma:
            return "BUY_SIGNAL", current_sma
        else:
            return "SELL_SIGNAL", current_sma
            
    except Exception as e:
        print(f"Errore nel recupero storico: {e}")
        price = get_sol_price()
        return "HOLD", price if price else 0.0
        
