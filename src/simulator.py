import json
import os
from datetime import datetime
from bot_logic import get_sol_price, analyze_market

PORTFOLIO_FILE = "src/portfolio.json"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {"cash": 30.00, "sol": 0.0, "initial_capital": 30.00}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def run_paper_trade():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] === Ciclo Portafoglio Paper Trading ($30) ===")
    
    price = get_sol_price()
    if not price:
        print("Impossibile procedere senza prezzo.")
        return

    portfolio = load_portfolio()
    cash = portfolio["cash"]
    sol = portfolio["sol"]
    
    signal, sma = analyze_market()
    print(f"Prezzo SOL: ${price:.2f} | SMA: ${sma:.2f} | Segnale: {signal}")
    print(f"Portafoglio attuale -> Cash: ${cash:.2f} | SOL: {sol:.4f}")

    total_value = cash + (sol * price)
    pnl = total_value - portfolio['initial_capital']
    print(f"Valore Totale: ${total_value:.2f} (P&L: {pnl:+.2f}$)")

    # Logica di simulazione acquisto/vendita
    if "BUY" in signal and cash > 2.0:
        amount_to_spend = cash
        sol_bought = amount_to_spend / price
        portfolio["sol"] += sol_bought
        portfolio["cash"] = 0.0
        print(f">>> [SIMULAZIONE ACQUISTO] Acquistati {sol_bought:.4f} SOL a ${price:.2f}")
    elif "SELL" in signal and sol > 0:
        cash_earned = sol * price
        portfolio["cash"] += cash_earned
        portfolio["sol"] = 0.0
        print(f">>> [SIMULAZIONE VENDITA] Venduti {sol:.4f} SOL a ${price:.2f} per ${cash_earned:.2f}")
    else:
        print(">>> [ATTesa] Nessuna modifica alla posizione attuale.")

    save_portfolio(portfolio)
    print("=== Fine ciclo completato con successo ===")

if __name__ == "__main__":
    run_paper_trade()
    
