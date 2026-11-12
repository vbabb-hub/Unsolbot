import json
import os
from datetime import datetime
from bot_logic import get_sol_market_data, analyze_market

PORTFOLIO_FILE = "src/portfolio.json"
README_FILE = "README.md"

def load_portfolio():
    if os.path.exists(PORTFOLIO_FILE):
        with open(PORTFOLIO_FILE, "r") as f:
            return json.load(f)
    return {"cash": 30.00, "sol": 0.0, "initial_capital": 30.00, "position_active": False, "entry_price": 0.0, "take_profit_price": 0.0}

def save_portfolio(portfolio):
    with open(PORTFOLIO_FILE, "w") as f:
        json.dump(portfolio, f, indent=4)

def update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg):
    """Scrive la dashboard completa direttamente sul file README.md del repository"""
    
    pos_status = "🟢 Posizione Aperta (In attesa di Take Profit)" if portfolio["position_active"] else "⚪ Nessuna Posizione (Liquidità disponibile)"
    entry = f"${portfolio['entry_price']:.2f}" if portfolio["position_active"] else "N/A"
    tp = f"${portfolio['take_profit_price']:.2f} (+5% Target)" if portfolio["position_active"] else "N/A"
    
    dashboard_content = f"""# 🤖 Dashboard Bot di Trading Solana ($30)

*Ultimo aggiornamento automatico:* `{timestamp} UTC`

---

## 💰 1. Capitale e Portafoglio
| Metrica | Valore |
| :--- | :--- |
| **Capitale Iniziale** | `$30.00` |
| **Liquidità Residua (Cash)** | **`${portfolio['cash']:.2f}`** |
| **Solana in Portafoglio** | `{portfolio['sol']:.4f} SOL` |
| **Valore Totale Portafoglio** | **${total_value:.2f}** |
| **Profitto / Perdita (P&L)** | **${pnl:+.2f}** ({ (pnl/30)*100:+.2f}% ) |

---

## 📈 2. Andamento di Solana (Timeframe)
| 1 Ora (1h) | 1 Giorno (1d) | 1 Settimana (1w) | 1 Mese (1m) | 1 Anno (1y) | All-Time High |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `{changes['1h']:+.2f}%` | `{changes['1d']:+.2f}%` | `{changes['1w']:+.2f}%` | `{changes['1m']:+.2f}%` | `{changes['1y']:+.2f}%` | `${changes['ath']:.2f}` |

*(Prezzo attuale SOL: **${price:.2f}**)*

---

## 📊 3. Posizioni Aperte & Regole (No Stop-Loss)
- **Stato:** `{pos_status}`
- **Prezzo di Entrata:** `{entry}`
- **Target Take Profit (TP):** `{tp}`
- **Politica di Gestione:** *HODL / Long-only (Nessuno Stop Loss applicato)*

---

## 🔬 4. Diagnostica Tecnica & Ultima Azione
- **Media Mobile (SMA 20):** `${sma:.2f}`
- **RSI (14):** `{rsi:.1f}`
- **Segnale Algoritmo:** `{signal}`
- **Ultima Azione Registrata:** `{action_msg}`

---
*Bot autonomo sviluppato in Python e schedulato tramite GitHub Actions (Modalità Paper Trading).*
"""
    with open(README_FILE, "w", encoding="utf-8") as f:
        f.write(dashboard_content)

def run_paper_trade():
    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{timestamp}] === Avvio Ciclo Bot Trading ===")
    
    price, changes = get_sol_market_data()
    if not price:
        print("Impossibile recuperare il prezzo di Solana.")
        return

    portfolio = load_portfolio()
    signal, sma, rsi = analyze_market()
    
    total_value = portfolio["cash"] + (portfolio["sol"] * price)
    pnl = total_value - portfolio['initial_capital']
    
    action_msg = "Nessuna operazione effettuata."

    # 1. Controllo Take Profit se c'è una posizione aperta (SENZA STOP LOSS)
    if portfolio["position_active"]:
        if price >= portfolio["take_profit_price"]:
            cash_earned = portfolio["sol"] * price
            portfolio["cash"] += cash_earned
            action_msg = f"🎯 Take Profit raggiunto a ${price:.2f}! Venduti {portfolio['sol']:.4f} SOL per ${cash_earned:.2f}"
            portfolio["sol"] = 0.0
            portfolio["position_active"] = False
            portfolio["entry_price"] = 0.0
            portfolio["take_profit_price"] = 0.0
            print(f">>> {action_msg}")
        else:
            action_msg = f"Posizione attiva. In attesa del TP (${portfolio['take_profit_price']:.2f}). Nessuno Stop Loss applicato."
            print(f">>> [HODL] {action_msg}")
            
    # 2. Controllo Segnale di Acquisto se siamo flat (liquidità disponibile)
    elif not portfolio["position_active"] and portfolio["cash"] > 2.0:
        if "BUY" in signal:
            amount_to_spend = portfolio["cash"]
            sol_bought = amount_to_spend / price
            portfolio["sol"] = sol_bought
            portfolio["cash"] = 0.0
            portfolio["position_active"] = True
            portfolio["entry_price"] = price
            portfolio["take_profit_price"] = price * 1.05  # Target +5%
            
            action_msg = f"🛒 Acquistati {sol_bought:.4f} SOL a ${price:.2f}. TP impostato a ${portfolio['take_profit_price']:.2f}."
            print(f">>> [ACQUISTO] {action_msg}")
        else:
            action_msg = "In attesa di segnale di ingresso valido."

    total_value = portfolio["cash"] + (portfolio["sol"] * price)
    pnl = total_value - portfolio['initial_capital']

    save_portfolio(portfolio)
    update_readme_dashboard(timestamp, price, changes, sma, rsi, signal, portfolio, total_value, pnl, action_msg)
    
    print("=== Ciclo completato con successo ===")

if __name__ == "__main__":
    run_paper_trade()
