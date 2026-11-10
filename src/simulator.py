from datetime import datetime
from bot_logic import get_sol_price, analyze_market

def run_paper_trade():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] === Avvio ciclo di Paper Trading Solana ===")
    
    price = get_sol_price()
    if not price:
        print("Impossibile procedere senza prezzo.")
        return

    signal = analyze_market()
    print(f"Esito analisi tecnica: {signal}")
    print("=== Fine ciclo (Simulazione completata con successo) ===")

if __name__ == "__main__":
    run_paper_trade()
