import json
import os
from datetime import datetime
from bot_logic import get_sol_price, analyze_market

PORTFOLIO_FILE = "src/portfolio.json"
REPORT_FILE = "report.md"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {"cash": 30.00, "sol": 0.0, "initial_capital": 30.00}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def update_markdown_report(timestamp, price, sma, rsi, signal, cash, sol, total_value, pnl, action_msg):
    """Aggiorna il file report.md con i dati di RSI e SMA"""
    report_content = f"""# 🤖 Report Paper Trading Solana ($30) - Strategia RSI + SMA

*Ultimo aggiornamento:* `{timestamp} UTC`

## 📊 Stato Attuale del Portafoglio
| Metrica | Valore |
| :--- | :--- |
| **Capitale Iniziale** | `$30.00` |
| **Liquidità (Cash)** | `${cash:.2f}` |
| **Solana Posseduti (SOL)** | `{sol:.4f} SOL` |
| **Valore Totale Portafoglio** | **${total_value:.2f}** |
| **Profitto / Perdita (P&L)** | **${pnl:+.2f}** |

---

## 📈 Ultima Analisi Tecnica
- **Prezzo Corrente SOL:** `${price:.2f}`
- **Media Mobile (SMA 20):** `${sma:.2f}`
- **RSI (14 periodi):** `{rsi:.1f}` {'🟢 (Ipervenduto)' if rsi < 35 else '🔴 (Ipercomprato)' if rsi > 70 else '⚪ (Neutro)'}
- **Segnale Generato:** `{signal}`
- **Azione Eseguita:** `{action_msg}`

---
*Bot autonomo eseguito tramite GitHub Actions.*
"""
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(report_content)

def run_paper_trade():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] === Ciclo Paper Trading RSI + SMA ($30) ===")
    
    price = get_sol_price()
    if not price:
        print("Impossibile procedere senza prezzo.")
        return

    portfolio = load_portfolio()
    cash = portfolio["cash"]
    sol = portfolio["sol"]
    
    signal, sma, rsi = analyze_market()
    print(f"Portafoglio attuale -> Cash: ${cash:.2f} | SOL: {sol:.4f}")

    total_value = cash + (sol * price)
    pnl = total_value - portfolio['initial_capital']
    print(f"Valore Totale: ${total_value:.2f} (P&L: {pnl:+.2f}$)")

    action_msg = "Nessuna azione eseguita (In attesa di condizioni ottimali)."

    # Logica di simulazione acquisto/vendita
    if "BUY" in signal and cash > 2.0:
        amount_to_spend = cash
        sol_bought = amount_to_spend / price
        portfolio["sol"] += sol_bought
        portfolio["cash"] = 0.0
        action_msg = f"Acquistati {sol_bought:.4f} SOL a ${price:.2f}"
        print(f">>> [SIMULAZIONE ACQUISTO] {action_msg}")
    elif "SELL" in signal and sol > 0:
        cash_earned = sol * price
        portfolio["cash"] += cash_earned
        portfolio["sol"] = 0.0
        action_msg = f"Venduti {sol:.4f} SOL a ${price:.2f} per ${cash_earned:.2f}"
        print(f">>> [SIMULAZIONE VENDITA] {action_msg}")
    else:
        print(">>> [ATTESA] Nessuna modifica alla posizione.")

    save_portfolio(portfolio)
    update_markdown_report(timestamp, price, sma, rsi, signal, portfolio["cash"], portfolio["sol"], total_value, pnl, action_msg)
    
    print("=== Fine ciclo completato con successo ===")

if __name__ == "__main__":
    run_paper_trade()
    
