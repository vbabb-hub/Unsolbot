import requests
import pandas as pd
import numpy as np

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

def calculate_rsi(series, period=14):
    """Calcola l'RSI (Relative Strength Index) in modo nativo"""
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market():
    """Scarica lo storico recente e calcola SMA e RSI"""
    url = "https://api.coingecko.com/api/v3/coins/solana/market_chart?vs_currency=usd&days=1"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        prices = [item[1] for item in data['prices']]
        
        df = pd.DataFrame(prices, columns=['close'])
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['rsi_14'] = calculate_rsi(df['close'], period=14)
        
        current_price = df['close'].iloc[-1]
        current_sma = df['sma_20'].iloc[-1]
        current_rsi = df['rsi_14'].iloc[-1]
        
        if pd.isna(current_sma):
            current_sma = current_price
        if pd.isna(current_rsi):
            current_rsi = 50.0  # Valore neutro di sicurezza
            
        print(f"Prezzo: ${current_price:.2f} | SMA(20): ${current_sma:.2f} | RSI(14): {current_rsi:.1f}")

        # Logica di trading avanzata RSI + SMA
        if current_rsi < 35:
            return "BUY_SIGNAL (RSI Ipervenduto - Possibile rimbalzo)", current_sma, current_rsi
        elif current_rsi > 70:
            return "SELL_SIGNAL (RSI Ipercomprato - Prendi profitto)", current_sma, current_rsi
        elif current_price > current_sma and current_rsi < 60:
            return "BUY_SIGNAL (Trend rialzista sopra SMA)", current_sma, current_rsi
        else:
            return "HOLD (Nessun segnale operativo)", current_sma, current_rsi
            
    except Exception as e:
        print(f"Errore nel recupero storico: {e}")
        price = get_sol_price()
        return "HOLD", price if price else 0.0, 50.0
        
