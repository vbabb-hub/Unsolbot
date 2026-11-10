import requests
import pandas as pd

def get_sol_price():
    """Recupera il prezzo corrente di SOL/USDT da CoinCap API (gratuito e accessibile da cloud)"""
    url = "https://api.coincap.io/v2/assets/solana"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        return float(data['data']['priceUsd'])
    except Exception as e:
        print(f"Errore nel recupero del prezzo da CoinCap: {e}")
        return None

def analyze_market():
    """Recupera dati storici recenti tramite CoinGecko o fallback a simulazione se indisponibile"""
    url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd&include_market_cap=false&include_24hr_vol=false&include_24hr_change=true"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        current_price = float(data['solana']['usd'])
        
        print(f"Prezzo corrente SOL (CoinGecko): ${current_price:.2f}")
        
        # Logica di test semplificata per il paper trading iniziale
        return "HOLD / ANALISI COMPLETATA (Prezzo verificato con successo)"
            
    except Exception as e:
        print(f"Errore nell'analisi dei dati: {e}")
        # Fallback sul prezzo singolo se fallisce lo storico
        price = get_sol_price()
        if price:
            print(f"Prezzo di emergenza SOL: ${price:.2f}")
            return "HOLD / PREZZO RECUPERATO"
        return "ERRORE"
        
