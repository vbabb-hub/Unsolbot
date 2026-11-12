import requests
import pandas as pd

def get_sol_market_data():
    """Recupera prezzo, variazioni percentuali e dati storici per Solana da CoinGecko"""
    url = "https://api.coingecko.com/api/v3/coins/solana?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()['market_data']
        
        current_price = data['current_price']['usd']
        changes = {
            "1h": data.get('price_change_percentage_1h_in_currency', {}).get('usd', 0.0),
            "1d": data.get('price_change_percentage_24h', 0.0),
            "1w": data.get('price_change_percentage_7d', 0.0),
            "1m": data.get('price_change_percentage_30d', 0.0),
            "1y": data.get('price_change_percentage_1y', 0.0),
            "ath": data.get('ath', {'usd': 0})['usd']
        }
        return current_price, changes
    except Exception as e:
        print(f"Errore recupero dati di mercato: {e}")
        # Fallback rapido sul prezzo base
        price_url = "https://api.coincap.io/v2/assets/solana"
        res = requests.get(price_url, timeout=5).json()
        return float(res['data']['priceUsd']), {"1h": 0, "1d": 0, "1w": 0, "1m": 0, "1y": 0, "ath": 0}

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def analyze_market():
    """Analisi tecnica per i segnali di acquisto e Take Profit (senza stop loss)"""
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
        
        if pd.isna(current_sma): current_sma = current_price
        if pd.isna(current_rsi): current_rsi = 50.0
            
        if current_rsi < 35:
            return "BUY_SIGNAL (RSI Ipervenduto)", current_sma, current_rsi
        elif current_price > current_sma and current_rsi < 60:
            return "BUY_SIGNAL (Trend Rialzista)", current_sma, current_rsi
        else:
            return "HOLD (Attesa)", current_sma, current_rsi
    except Exception as e:
        print(f"Errore analisi tecnica: {e}")
        return "HOLD", 0.0, 50.0
