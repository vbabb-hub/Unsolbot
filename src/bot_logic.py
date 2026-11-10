import requests
import pandas as pd

def get_sol_price():
    """Recupera il prezzo corrente di SOL/USDT da Binance (100% gratuito, senza API key)"""
    url = "https://api.binance.com/api/v3/ticker/price?symbol=SOLUSDT"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        print(f"Errore nel recupero del prezzo: {e}")
        return None

def analyze_market():
    """Simula l'analisi tecnica di base (es. recupero candele storiche recenti)"""
    url = "https://api.binance.com/api/v3/klines?symbol=SOLUSDT&interval=15m&limit=20"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        # Converte in DataFrame pandas
        df = pd.DataFrame(data, columns=[
            'open_time', 'open', 'high', 'low', 'close', 'volume',
            'close_time', 'quote_asset_volume', 'number_of_trades',
            'taker_buy_base', 'taker_buy_quote', 'ignore'
        ])
        
        df['close'] = df['close'].astype(float)
        
        # Calcolo di una semplice SMA a 10 periodi
        df['sma_10'] = df['close'].rolling(window=10).mean()
        
        current_price = df['close'].iloc[-1]
        current_sma = df['sma_10'].iloc[-1]
        
        print(f"Prezzo corrente SOL: ${current_price:.2f}")
        print(f"SMA (15m) corrente: ${current_sma:.2f}")
        
        # Logica di esempio per il segnale
        if current_price > current_sma:
            return "HOLD / BUY_SIGNAL (Prezzo sopra la media)"
        else:
            return "WAIT / SELL_SIGNAL (Prezzo sotto la media)"
            
    except Exception as e:
        print(f"Errore nell'analisi dei dati storici: {e}")
        return "ERRORE"
